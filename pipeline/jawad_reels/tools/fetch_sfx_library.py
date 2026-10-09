#!/usr/bin/env python3
"""fetch_sfx_library.py - re-download the CC0 / public-domain sample kit that epic_sfx.py's *_real sounds read.

Spec: brand_reels/research/sound_design.md section 2 (sources) and section 3 (the 11 sample sounds). The kit is git-ignored
data; this script is the committed recipe that rebuilds it, with a per-file licence record.

    python3 -I pipeline/jawad_reels/tools/fetch_sfx_library.py [--lib DIR] [--only kenney,opengameart,wikimedia]
                                    [--extras] [--force] [--dry-run] [--no-copy] [--no-kit-links]
                                    [--wm-budget SECONDS] [--no-transcode]

Sources (CC0 / public domain ONLY; never freesound, pixabay, BBC, CC-BY or BY-SA):
    kenney/<pack>/...           Kenney.nl audio packs interface-sounds, impact-sounds, ui-audio, sci-fi-sounds, digital-audio
                                (CC0 1.0, License.txt inside every zip; the zip link is read from the asset page)
    opengameart/<item>/...      six OpenGameArt items whose page lists CC0: crowd_shouting (StarNinjas), applause_church
                                (eXpl0it3r), crowd_ooo (Nocturnal_Vanguard), rain_loopable (Ylmir), traffic_road (IgnasD),
                                sfx_loops (rubberduck, "30 CC0 SFX loops")
    wikimedia/<group>/...       six Wikimedia Commons files whose licence is CC0 or public domain (most from the old PDSounds
                                archive): Ohhh ahhh, Slow starting applause, Rain and thunder, Clock ticking, Typing - Model M
                                1986, Laptop keyboard. --extras adds Tick2 (CC0, 3 MB), Rain and thunder (1) (PD) and the
                                stereo "Light Rain Distant Thunder July 5th 2016" (CC0, 42 MB), which section 7.3 left queued.
The reel modules read two of these paths directly (keep them exactly): opengameart/crowd_shouting/crowd_shouting_0.ogg and
wikimedia/crowd/Ohhh_ahhh.ogg.

Outputs (default library = <repo>/workspace/brand_reels/sfx/library, or $EPIC_SFX_LIB):
    library/<source>/...         the files (one folder per source; zips are unpacked and deleted)
    library/manifest.json        every file: path, bytes, sha256, source, page / file URL, author, licence
    library/wikimedia/manifest.json   the Commons records (title, file page, original URL, sha1, licence, artist, credit)
    library/LICENSES.md          the human-readable licence record (deterministic: no dates, sorted)
    pipeline/jawad_reels/sfx_library_LICENSES.md   a copy of LICENSES.md for the repo (--no-copy to skip)
    <library>/../epic_{sfx,music,mix}.py   relative symlinks to the committed kit in pipeline/jawad_reels (the reel music
                                 modules hash these legacy paths in their reports); never replaces a regular file
                                 (--no-kit-links to skip)

Behaviour:
    * idempotent: a file whose bytes match the manifest (size + sha256; Commons: the API's sha1) and that ffprobe decodes is
      never downloaded again; --force re-downloads everything
    * polite: one request at a time, a minimum gap per host (Commons API 3 s, upload.wikimedia.org 10 s), a descriptive
      User-Agent, retries with exponential backoff on 429 / 5xx / time-outs / HTML error pages, honouring Retry-After;
      the Commons metadata is ONE batched API query, its records cached in wikimedia/commons_api.json
    * Wikimedia rate limits never block the run: upload.wikimedia.org answers shared IPs with HTML 429 pages and
      Retry-After: 600, so the Wikimedia stage spends at most --wm-budget seconds (default 240) in all. A file whose
      original stays rate-limited falls back to Commons' own MP3 transcode of it (same recording, same licence; duration
      checked against the API record; stored as <file>.mp3, --no-transcode to skip); otherwise it is QUEUED: listed in
      LICENSES.md and wikimedia/manifest.json, and the *_real sound that needs it does not register until a later run
      fetches it
    * every licence is re-checked at fetch time (Kenney License.txt says CC0, the OpenGameArt page's licence field lists
      CC0, the Commons extmetadata licence is CC0 or public domain; a cached API record counts, it was checked when it was
      read); anything else is refused
    * downloads are untrusted data: written only into their source folder, checked by magic bytes (an HTML page is
      rejected), decoded only by ffprobe / ffmpeg, never executed or imported; zips are unpacked by this script with
      path, type, size and ratio limits (audio + licence text only). Run with python3 -I (the script re-executes itself
      under -I when it is not)
Exit status 0 when every required file (Kenney, OpenGameArt and the two paths the reel modules read) is present and
verified, 1 otherwise; queued optional Wikimedia files are reported but do not fail the run.
"""
import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

if not sys.flags.isolated:                 # untrusted downloads: never run with the cwd / script dir on sys.path
    os.execv(sys.executable, [sys.executable, '-I'] + sys.argv)

HERE = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.dirname(HERE)                                   # pipeline/jawad_reels
REPO = os.path.abspath(os.path.join(PIPE, '..', '..'))
DEFAULT_LIB = os.path.join(REPO, 'workspace', 'brand_reels', 'sfx', 'library')
LICENSE_COPY = os.path.join(PIPE, 'sfx_library_LICENSES.md')
KIT_MODULES = ('epic_sfx.py', 'epic_music.py', 'epic_mix.py')
UA = ('JawadReelsSfxKit/1.0 (CC0/PD sample-kit fetcher for a private video project; low volume, one request at a time) '
      'Python-urllib/%d.%d' % sys.version_info[:2])
AUDIO_EXT = ('.ogg', '.oga', '.wav', '.mp3', '.flac')
TEXT_EXT = ('.txt',)
MAX_FILE = 80 * 1024 * 1024                # largest single file accepted (the 42 MB Commons rain extra fits)
MAX_ZIP_TOTAL = 200 * 1024 * 1024
HOST_GAP = {'commons.wikimedia.org': 3.0, 'upload.wikimedia.org': 10.0, 'opengameart.org': 1.5, 'kenney.nl': 1.0}
RETRY_CAP = 900.0                          # longest single wait (s) when a server asks us to back off

# ============================================================================================ the kit
KENNEY = [  # pack, expected file count (asset page), fallback zip URL (the asset page is read first)
    ('interface-sounds', 100, 'https://kenney.nl/media/pages/assets/interface-sounds/fa43c1dd4d-1677589452/'
                              'kenney_interface-sounds.zip'),
    ('impact-sounds', 130, 'https://kenney.nl/media/pages/assets/impact-sounds/87b4ddecda-1677589768/'
                           'kenney_impact-sounds.zip'),
    ('ui-audio', 50, 'https://kenney.nl/media/pages/assets/ui-audio/490d233f68-1677590494/kenney_ui-audio.zip'),
    ('sci-fi-sounds', 70, 'https://kenney.nl/media/pages/assets/sci-fi-sounds/6b296f9ecf-1677589334/'
                          'kenney_sci-fi-sounds.zip'),
    ('digital-audio', 60, 'https://kenney.nl/media/pages/assets/digital-audio/216eac4753-1677590265/'
                          'kenney_digital-audio.zip'),
]
OGA_FILES = 'https://opengameart.org/sites/default/files/'
OPENGAMEART = [  # folder, item page, title, author, [(remote file name, local name)], zip?
    dict(key='crowd_shouting', page='https://opengameart.org/content/crowd-shoutingspeaking-ambience',
         title='Crowd shouting/speaking ambience', author='StarNinjas',
         files=[('crowd_shouting_0.ogg', 'crowd_shouting_0.ogg')]),
    dict(key='applause_church', page='https://opengameart.org/content/applause-in-a-large-hall-or-church',
         title='Applause in a large hall or church', author='eXpl0it3r',
         files=[('applause-clapping-church-crowd-immersive.wav', 'applause-clapping-church-crowd-immersive.wav')]),
    dict(key='crowd_ooo', page='https://opengameart.org/content/oooooooooooooo', title='OoOoOoOoOoOoOo',
         author='Nocturnal_Vanguard (AuraVoice)', files=[('oooooooooo.ogg', 'oooooooooo.ogg')]),
    dict(key='rain_loopable', page='https://opengameart.org/content/rain-loopable', title='Rain (loopable)',
         author='Ylmir', files=[('Rain OGG.zip', None)]),
    dict(key='traffic_road', page='https://opengameart.org/content/high-traffic-road-sounds',
         title='High traffic road sounds', author='IgnasD', files=[('gatve Varniu_2.ogg', 'gatve_Varniu.ogg')]),
    dict(key='sfx_loops', page='https://opengameart.org/content/30-cc0-sfx-loops', title='30 CC0 SFX loops',
         author='rubberduck', files=[('sfx_loops.zip', None)]),
]
WIKIMEDIA = [  # Commons title, local path under wikimedia/, used by
    ('File:Ohhh ahhh.ogg', 'crowd/Ohhh_ahhh.ogg', 'crowd_ahh_real; log_kya_kahenge_sfx whisper wall'),
    ('File:Slow starting applause.ogg', 'crowd/Slow_starting_applause.ogg', 'applause_build_real'),
    ('File:Rain and thunder.ogg', 'rain/Rain_and_thunder.ogg', 'rain_thunder_real'),
    ('File:Clock ticking.ogg', 'clock/Clock_ticking.ogg', 'clock_real'),
    ('File:Typing - Model M 1986.ogg', 'typing/Typing_-_Model_M_1986.ogg', 'typing_modelm_real'),
    ('File:Laptop keyboard.ogg', 'typing/Laptop_keyboard.ogg', '(kit: laptop typing)'),
]
WIKIMEDIA_EXTRAS = [
    ('File:Tick2.ogg', 'clock/Tick2.ogg', '(extra: small clock)'),
    ('File:Rain and thunder (1).ogg', 'rain/Rain_and_thunder_1.ogg', '(extra: 60 s rain + thunder)'),
    ('File:Light Rain Distant Thunder July 5th 2016.wav', 'rain/Light_Rain_Distant_Thunder_July_5th_2016.wav',
     '(extra: stereo rain, 42 MB)'),
]
WM_OK_LICENCES = {'cc0', 'pd', 'public domain', 'cc-zero', 'cc0 1.0'}
USED_BY = {  # which sounds / reel modules read which file (epic_sfx.SAMPLES is the authority for the sounds)
    'opengameart/crowd_shouting/crowd_shouting_0.ogg': 'crowd_cheer_real (contains English speech: "Oh my God, look at '
                                                       'that!"); bijli_chali_gayi_sfx mohalla_cheer; log_kya_kahenge_sfx '
                                                       'whisper wall (both read this path directly)',
    'opengameart/applause_church/applause-clapping-church-crowd-immersive.wav': 'applause_real',
    'opengameart/crowd_ooo/oooooooooo.ogg': 'crowd_ooh_real',
    'opengameart/traffic_road/gatve_Varniu.ogg': 'traffic_real',
    'opengameart/rain_loopable/1.ogg': 'rain_real',
    'kenney/impact-sounds/Audio/impactBell_heavy_000.ogg': 'bell_impact_real',
}
REEL_PATHS = ('opengameart/crowd_shouting/crowd_shouting_0.ogg', 'wikimedia/crowd/Ohhh_ahhh.ogg')  # read by reel modules


# ============================================================================================ small utilities
def log(*a):
    print(*a, flush=True)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def sha1_of(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def strip_tags(s):
    s = re.sub(r'<[^>]+>', ' ', s or '')
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()


def safe_name(part):
    """One path component of a downloaded name -> a plain file name (letters, digits, . _ - only)."""
    part = re.sub(r'\s+', '_', part.strip())
    part = re.sub(r'[^A-Za-z0-9._()\-]', '_', part)
    part = part.lstrip('.') or '_'
    return part[:120]


def within(path, root):
    path, root = os.path.realpath(path), os.path.realpath(root)
    return path == root or path.startswith(root + os.sep)


class RateLimited(RuntimeError):
    """The server keeps answering 429 (or asks for a wait that does not fit the time budget)."""


class Net:
    """Sequential HTTP client: per-host minimum gap, retries with backoff (429 / 5xx / time-outs / HTML pages)."""

    def __init__(self, dry=False):
        self.last = {}
        self.dry = dry
        self.requests = 0
        self.rate_limited = 0

    def _wait(self, host):
        gap = HOST_GAP.get(host, 1.0)
        dt = time.time() - self.last.get(host, 0.0)
        if dt < gap:
            time.sleep(gap - dt)
        self.last[host] = time.time()

    def get(self, url, binary=True, tries=7, max_bytes=MAX_FILE, to_file=None, deadline=None, max_wait=RETRY_CAP):
        """GET url -> bytes (or streams into to_file and returns its size). binary=True rejects an HTML body.
        deadline (time.time() value): never wait past it; a retry that would is abandoned with RateLimited (HTTP 429)
        or RuntimeError. max_wait caps one back-off wait (a longer Retry-After counts as 'does not fit')."""
        host = urllib.parse.urlsplit(url).hostname or ''
        err = None
        last_code = None
        for k in range(tries):
            if deadline is not None and time.time() > deadline:
                break
            self._wait(host)
            self.requests += 1
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    ctype = (r.headers.get('Content-Type') or '').lower()
                    if binary and 'text/html' in ctype:
                        raise ValueError('HTML page instead of a file (%s)' % ctype)
                    if to_file:
                        n = 0
                        with open(to_file, 'wb') as fo:
                            while True:
                                b = r.read(1 << 16)
                                if not b:
                                    break
                                n += len(b)
                                if n > max_bytes:
                                    raise ValueError('file larger than %d bytes' % max_bytes)
                                fo.write(b)
                        if binary and looks_html(to_file):
                            raise ValueError('HTML page instead of a file')
                        return n
                    data = r.read(max_bytes + 1)
                    if len(data) > max_bytes:
                        raise ValueError('response larger than %d bytes' % max_bytes)
                    if binary and data[:1024].lstrip().lower().startswith((b'<!doctype', b'<html', b'<')):
                        raise ValueError('HTML page instead of a file')
                    return data
            except urllib.error.HTTPError as e:
                err = 'HTTP %d' % e.code
                last_code = e.code
                if e.code in (401, 403, 404, 405, 407, 410):
                    raise RuntimeError('%s for %s (not retried)' % (err, url))
                ra = e.headers.get('Retry-After') if e.headers else None
                wait = float(ra) if ra and ra.strip().isdigit() else 5.0 * 2 ** k
                if e.code == 429:
                    self.rate_limited += 1
            except (urllib.error.URLError, TimeoutError, ConnectionError, ValueError, OSError) as e:
                err = '%s: %s' % (type(e).__name__, e)
                last_code = None
                wait = 5.0 * 2 ** k
            wait = wait + 2.0                                  # honour Retry-After (upload.wikimedia.org: 600 s)
            if k >= tries - 1:
                break
            if wait > max_wait or (deadline is not None and time.time() + wait > deadline):
                log('    %s: a %.0f s back-off does not fit the time budget, giving up on this URL for now' % (err, wait))
                break
            log('    retry %d/%d in %.0f s (%s)' % (k + 1, tries - 1, wait, err))
            time.sleep(wait)
        if last_code == 429:
            raise RateLimited('rate-limited (HTTP 429): %s' % url)
        raise RuntimeError('gave up after %d tries: %s (%s)' % (tries, url, err))


MAGIC = {'.ogg': [b'OggS'], '.oga': [b'OggS'], '.flac': [b'fLaC'], '.wav': [b'RIFF'], '.zip': [b'PK\x03\x04'],
         '.mp3': [b'ID3', b'\xff\xfb', b'\xff\xf3', b'\xff\xf2', b'\xff\xfa', b'\xff\xe3']}


def head_bytes(path, n):
    with open(path, 'rb') as f:
        return f.read(n)


def looks_html(path):
    with open(path, 'rb') as f:
        head = f.read(2048).lstrip().lower()
    return head.startswith(b'<') or b'<html' in head[:512] or b'<!doctype html' in head[:512]


def magic_ok(path):
    ext = os.path.splitext(path)[1].lower()
    with open(path, 'rb') as f:
        head = f.read(16)
    if ext == '.wav':
        return head[:4] == b'RIFF' and head[8:12] == b'WAVE'
    return any(head.startswith(m) for m in MAGIC.get(ext, [b'']))


def ffprobe(path):
    """-> dict(duration, codec, sr, channels) or None when it is not decodable audio."""
    try:
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                            'format=duration,format_name:stream=codec_type,codec_name,sample_rate,channels', '-of',
                            'json', path], capture_output=True, text=True, timeout=60)
        d = json.loads(r.stdout or '{}')
    except Exception:
        return None
    st = [s for s in d.get('streams', []) if s.get('codec_type') == 'audio']
    try:
        dur = float(d.get('format', {}).get('duration') or 0.0)
    except ValueError:
        dur = 0.0
    if r.returncode != 0 or not st or dur <= 0.002:          # Kenney has genuine 10 ms clicks
        return None
    s = st[0]
    return dict(duration=round(dur, 3), codec=s.get('codec_name'), sr=int(s.get('sample_rate') or 0),
                channels=int(s.get('channels') or 0))


def verify_audio(path):
    """Magic bytes + not HTML + ffprobe decodes it. -> probe dict or raises ValueError."""
    if looks_html(path):
        raise ValueError('%s is an HTML page' % path)
    if not magic_ok(path):
        raise ValueError('%s has the wrong magic bytes for its type' % path)
    p = ffprobe(path)
    if p is None:
        raise ValueError('%s does not decode with ffprobe' % path)
    return p


def safe_extract(zpath, dest, keep_ext=AUDIO_EXT + TEXT_EXT):
    """Unpack only audio files and licence text from an untrusted zip into dest: no absolute / '..' paths, no
    symlinks, member and total size limits, compression ratio <= 200. Returns the extracted relative paths."""
    out = []
    total = 0
    with zipfile.ZipFile(zpath) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            raw = info.filename.replace('\\', '/')
            parts = [p for p in raw.split('/') if p not in ('', '.')]
            if not parts or raw.startswith('/') or any(p == '..' for p in parts) or ':' in raw:
                raise ValueError('unsafe member path %r in %s' % (raw, zpath))
            if ((info.external_attr >> 16) & 0o170000) == 0o120000:
                raise ValueError('symlink member %r in %s' % (raw, zpath))
            if parts[0] == '__MACOSX' or parts[-1].startswith('._'):
                continue
            ext = os.path.splitext(parts[-1])[1].lower()
            if ext not in keep_ext:
                continue
            if info.file_size > MAX_FILE:
                raise ValueError('member %r too large' % raw)
            total += info.file_size
            if total > MAX_ZIP_TOTAL:
                raise ValueError('%s unpacks to more than %d bytes' % (zpath, MAX_ZIP_TOTAL))
            if info.compress_size and info.file_size / max(info.compress_size, 1) > 200:
                raise ValueError('member %r has a suspicious compression ratio' % raw)
            rel = os.path.join(*[safe_name(p) for p in parts])
            dst = os.path.join(dest, rel)
            if not within(dst, dest):
                raise ValueError('member %r escapes %s' % (raw, dest))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            tmp = dst + '.part'
            n = 0
            with z.open(info) as src, open(tmp, 'wb') as fo:
                while True:
                    b = src.read(1 << 16)
                    if not b:
                        break
                    n += len(b)
                    if n > info.file_size or n > MAX_FILE:
                        raise ValueError('member %r is larger than declared' % raw)
                    fo.write(b)
            os.replace(tmp, dst)
            out.append(rel)
    return sorted(out)


# ============================================================================================ manifest
class Manifest:
    def __init__(self, lib):
        self.lib = lib
        self.path = os.path.join(lib, 'manifest.json')
        try:
            with open(self.path) as f:
                self.files = {e['path']: e for e in json.load(f).get('files', [])}
        except Exception:
            self.files = {}
        self.seen = set()

    def ok(self, rel):
        """True when rel exists and matches its manifest entry (size + sha256) and still decodes."""
        e = self.files.get(rel)
        p = os.path.join(self.lib, rel)
        if not e or not os.path.isfile(p) or os.path.getsize(p) != e.get('bytes'):
            return False
        if sha256_of(p) != e.get('sha256'):
            return False
        if os.path.splitext(p)[1].lower() in AUDIO_EXT:
            try:
                verify_audio(p)
            except ValueError:
                return False
        return True

    def add(self, rel, **meta):
        p = os.path.join(self.lib, rel)
        e = dict(path=rel, bytes=os.path.getsize(p), sha256=sha256_of(p))
        if os.path.splitext(p)[1].lower() in AUDIO_EXT:
            e['probe'] = verify_audio(p)
        e.update(meta)
        self.files[rel] = e
        self.seen.add(rel)
        return e

    def keep(self, rel):
        self.seen.add(rel)

    def save(self):
        files = [self.files[k] for k in sorted(self.files) if os.path.isfile(os.path.join(self.lib, k))]
        tmp = self.path + '.part'
        with open(tmp, 'w') as f:
            json.dump(dict(generator='pipeline/jawad_reels/tools/fetch_sfx_library.py', files=files), f, indent=1)
        os.replace(tmp, self.path)
        return files


# ============================================================================================ sources
def fetch_kenney(net, man, lib, force=False):
    errors = []
    for pack, count, fallback in KENNEY:
        page = 'https://kenney.nl/assets/' + pack
        dest = os.path.join(lib, 'kenney', pack)
        rels = sorted(k for k, e in man.files.items() if e.get('source') == 'kenney' and e.get('pack') == pack)
        if not force and rels and all(man.ok(k) for k in rels) and \
                sum(k.endswith(AUDIO_EXT) for k in rels) >= count:
            for k in rels:
                man.keep(k)
            log('  kenney/%s: %d files present, verified' % (pack, len(rels)))
            continue
        log('  kenney/%s: reading %s' % (pack, page))
        url = fallback
        try:
            h = net.get(page, binary=False).decode('utf-8', 'replace')
            m = re.findall(r"https://kenney\.nl/media/pages/assets/%s/[A-Za-z0-9_-]+/kenney_%s\.zip" %
                           (re.escape(pack), re.escape(pack)), h)
            if m:
                url = m[0]
            if 'Creative Commons CC0' not in h and 'CC0' not in h:
                raise RuntimeError('the asset page no longer states CC0')
        except RuntimeError as e:
            if 'CC0' in str(e):
                errors.append('kenney/%s: %s' % (pack, e))
                continue
            log('    asset page not readable (%s): using the recorded zip URL' % e)
        os.makedirs(dest, exist_ok=True)
        zp = os.path.join(dest, 'kenney_%s.zip.part' % pack)
        try:
            net.get(url, to_file=zp)
            if head_bytes(zp, 4) != b'PK\x03\x04':
                raise ValueError('the download is not a zip')
            with zipfile.ZipFile(zp) as z:
                lic = [i for i in z.namelist() if os.path.basename(i).lower() == 'license.txt']
                txt = z.read(lic[0]).decode('utf-8', 'replace') if lic else ''
            if not re.search(r'CC0|Creative Commons Zero|public domain', txt, re.I):
                raise ValueError('License.txt does not state CC0')
            got = safe_extract(zp, dest)
        except (RuntimeError, ValueError, zipfile.BadZipFile) as e:
            errors.append('kenney/%s: %s' % (pack, e))
            continue
        finally:
            if os.path.exists(zp):
                os.remove(zp)
        bad = 0
        for rel in got:
            full = os.path.join('kenney', pack, rel)
            try:
                man.add(full, source='kenney', pack=pack, page=page, url=url, author='Kenney (www.kenney.nl)',
                        licence='CC0 1.0 (License.txt in the pack)', title='Kenney %s' % pack)
            except ValueError as e:
                bad += 1
                errors.append(str(e))
        na = sum(r.endswith(AUDIO_EXT) for r in got)
        log('    %d audio files + licence text extracted (%d failed verification)' % (na, bad))
        if na < count:
            errors.append('kenney/%s: %d audio files, the asset page lists %d' % (pack, na, count))
    return errors


def _oga_licences(h):
    i = h.find('License(s):')
    seg = h[i:i + 3000] if i >= 0 else ''
    return sorted(set(re.findall(r"class='license-name'>([^<]+)<", seg) + re.findall(r'class="license-name">([^<]+)<',
                                                                                        seg)))


def fetch_opengameart(net, man, lib, force=False):
    errors = []
    for item in OPENGAMEART:
        dest = os.path.join(lib, 'opengameart', item['key'])
        rels = sorted(k for k, e in man.files.items() if e.get('source') == 'opengameart' and
                      e.get('item') == item['key'])
        if not force and rels and all(man.ok(k) for k in rels):
            for k in rels:
                man.keep(k)
            log('  opengameart/%s: %d file(s) present, verified' % (item['key'], len(rels)))
            continue
        log('  opengameart/%s: %s' % (item['key'], item['page']))
        try:
            h = net.get(item['page'], binary=False).decode('utf-8', 'replace')
        except RuntimeError as e:
            errors.append('opengameart/%s: page not readable: %s' % (item['key'], e))
            continue
        lic = _oga_licences(h)
        if 'CC0' not in [x.strip() for x in lic]:
            errors.append('opengameart/%s: the page licence is %s, not CC0: refused' % (item['key'], lic or '?'))
            continue
        os.makedirs(dest, exist_ok=True)
        for remote, local in item['files']:
            q = urllib.parse.quote(remote)
            url = OGA_FILES + q
            if q not in h and remote not in h:
                errors.append('opengameart/%s: %s is no longer linked on the page' % (item['key'], remote))
                continue
            meta = dict(source='opengameart', item=item['key'], page=item['page'], url=url, author=item['author'],
                        title=item['title'], licence='CC0 (OpenGameArt licence field: %s)' % ', '.join(lic))
            ext = os.path.splitext(remote)[1].lower()
            tmp = os.path.join(dest, safe_name(remote) + '.part')
            try:
                net.get(url, to_file=tmp)
                if ext == '.zip':
                    if head_bytes(tmp, 4) != b'PK\x03\x04':
                        raise ValueError('%s is not a zip' % remote)
                    got = safe_extract(tmp, dest)
                    for rel in got:
                        man.add(os.path.join('opengameart', item['key'], rel), archive=remote, **meta)
                    log('    %s: %d files extracted' % (remote, len(got)))
                else:
                    dst = os.path.join(dest, local)
                    os.replace(tmp, dst)
                    verify_audio(dst)
                    man.add(os.path.join('opengameart', item['key'], local), **meta)
                    log('    %s -> %s (%.2f MB)' % (remote, local, os.path.getsize(dst) / 1e6))
            except (RuntimeError, ValueError, zipfile.BadZipFile) as e:
                errors.append('opengameart/%s: %s' % (item['key'], e))
            finally:
                if os.path.exists(tmp):
                    os.remove(tmp)
    return errors


def _wm_licence_ok(em):
    """(ok, short, code, why) for a Commons extmetadata dict: only CC0 / public domain pass."""
    g = lambda k: strip_tags(em.get(k, {}).get('value', ''))
    lic_short, lic = g('LicenseShortName'), g('License').lower()
    if lic_short.lower() not in WM_OK_LICENCES and lic not in WM_OK_LICENCES:
        return False, lic_short, lic, 'licence %r / %r is not CC0 / public domain' % (lic_short, lic)
    if re.search(r'\b(by|sa|nc|nd)\b', lic) and lic not in WM_OK_LICENCES:
        return False, lic_short, lic, 'licence %r has conditions' % lic
    return True, lic_short, lic, ''


def _transcode_url(url):
    """Commons' own MP3 transcode of an original audio file (TimedMediaHandler derivative, same host), e.g.
    .../commons/a/a3/X.ogg -> .../commons/transcoded/a/a3/X.ogg/X.ogg.mp3. It is a re-encode of the same CC0 / PD
    recording (same licence), used only when the original keeps answering 429."""
    m = re.match(r'(https://upload\.wikimedia\.org/wikipedia/commons)/([0-9a-f])/([0-9a-f]{2})/([^/?#]+)$', url)
    if not m:
        return None
    base, h1, h2, name = m.groups()
    return '%s/transcoded/%s/%s/%s/%s.mp3' % (base, h1, h2, name, name)


def fetch_wikimedia(net, man, lib, extras=False, force=False, budget=240.0, transcode=True):
    """The Commons files: ONE batched API query (licence + sha1 + URL), its records cached in
    wikimedia/commons_api.json (a later run that cannot reach the API still has the licence verified at fetch time),
    then each original (sha1 must match). upload.wikimedia.org rate-limits by IP with HTML 429 pages and
    Retry-After 600: this stage never waits longer than `budget` seconds in all; a file whose original stays
    rate-limited falls back to Commons' MP3 transcode of it (--no-transcode to skip; duration checked against the API)
    and otherwise is left QUEUED (listed in LICENSES.md and wikimedia/manifest.json; rerun the fetcher later).
    Returns (errors, queued)."""
    errors, queued = [], []
    items = WIKIMEDIA + (WIKIMEDIA_EXTRAS if extras else [])
    dest = os.path.join(lib, 'wikimedia')
    mpath = os.path.join(dest, 'manifest.json')
    cpath = os.path.join(dest, 'commons_api.json')
    deadline = time.time() + max(0.0, float(budget))
    try:
        with open(mpath) as f:
            wman = {e['title']: e for e in json.load(f).get('files', [])}
    except Exception:
        wman = {}
    try:
        with open(cpath) as f:
            api_cache = json.load(f).get('records', {})
    except Exception:
        api_cache = {}

    def present(it):
        title, rel, _ = it
        e = wman.get(title)
        if not e or not man.ok(e['path']):
            return False
        p = os.path.join(lib, e['path'])
        if e.get('variant') == 'transcode-mp3':
            return True                                   # a transcode has no Commons sha1; size + sha256 checked
        return e.get('sha1') == sha1_of(p)
    todo = [it for it in items if force or not present(it)]
    for it in items:
        if it not in todo:
            e = wman[it[0]]
            man.keep(e['path'])
            log('  wikimedia/%s: present, verified%s' % (e['path'][10:], ' (Commons MP3 transcode)'
                                                          if e.get('variant') == 'transcode-mp3' else ''))
    if not todo:
        _save_wman(wman, lib, mpath, [])
        return errors, queued
    log('  wikimedia: one batched Commons API query for %d file(s) (time budget %.0f s)' % (len(todo), budget))
    q = dict(action='query', format='json', prop='imageinfo', iiprop='url|size|mime|sha1|extmetadata',
             iiextmetadatafilter='LicenseShortName|License|UsageTerms|Artist|Credit|ImageDescription|LicenseUrl',
             iiextmetadatalanguage='en', titles='|'.join(t for t, _, _ in todo))
    pages = {}
    try:
        d = json.loads(net.get('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(q), binary=False,
                               tries=5, deadline=deadline, max_wait=min(120.0, budget)).decode('utf-8'))
        norm = {n['from']: n['to'] for n in d.get('query', {}).get('normalized', [])}
        byt = {p.get('title'): p for p in d.get('query', {}).get('pages', {}).values()}
        for title, rel, used in todo:
            p = byt.get(norm.get(title, title))
            ii = (p or {}).get('imageinfo') or []
            if ii:
                pages[title] = ii[0]
                api_cache[title] = dict(ii[0], fetched_by='pipeline/jawad_reels/tools/fetch_sfx_library.py')
            elif p is not None:
                errors.append('wikimedia: %s not found on Commons' % title)
        os.makedirs(dest, exist_ok=True)
        with open(cpath + '.part', 'w') as f:
            json.dump(dict(note='Commons API imageinfo records (licence, sha1, URL) as read by the fetcher; used when '
                                'the API is unreachable', records={k: api_cache[k] for k in sorted(api_cache)}),
                      f, indent=1)
        os.replace(cpath + '.part', cpath)
    except (RuntimeError, ValueError) as e:
        log('  wikimedia: Commons API not readable (%s): using the cached API records (%d)' % (e, len(api_cache)))
        pages = {t: api_cache[t] for t, _, _ in todo if t in api_cache}
    for title, rel, used in todo:
        ii = pages.get(title)
        if not ii:
            queued.append(dict(title=title, path='wikimedia/' + rel, used_by=used,
                               reason='Commons API unreachable and no cached record (licence not verified yet)'))
            continue
        em = ii.get('extmetadata', {})
        g = lambda k: strip_tags(em.get(k, {}).get('value', ''))
        ok, lic_short, lic, why = _wm_licence_ok(em)
        if not ok:
            errors.append('wikimedia: %s %s: refused' % (title, why))
            continue
        url = ii['url'].split('?')[0]
        dst = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        tmp = dst + '.part'
        variant, got, why_q = 'original', None, ''
        try:
            if not force and os.path.isfile(dst) and sha1_of(dst) == ii.get('sha1'):
                log('  wikimedia/%s: on disk, sha1 matches Commons' % rel)
                got = dst
            elif time.time() >= deadline:
                why_q = 'Wikimedia time budget used up before this file'
            else:
                log('  wikimedia/%s <- %s (%.2f MB)' % (rel, url, ii.get('size', 0) / 1e6))
                for attempt in range(3):    # a truncated / rate-limit body fails the sha1: fetch again, slowly
                    net.get(url, to_file=tmp, tries=3, deadline=deadline, max_wait=min(90.0, budget))
                    if sha1_of(tmp) == ii.get('sha1'):
                        break
                    log('    sha1 mismatch (truncated or rate-limited body), retrying')
                    time.sleep(10.0 * (attempt + 1))
                else:
                    raise ValueError('sha1 never matched the Commons record')
                os.replace(tmp, dst)
                got = dst
        except RateLimited as e:
            why_q = 'upload.wikimedia.org answered 429 (rate limit) for the original'
            log('    %s' % e)
        except (RuntimeError, ValueError) as e:
            errors.append('wikimedia/%s: %s' % (rel, e))
            continue
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
        if got is None and transcode and why_q.startswith('upload') and _transcode_url(url):
            turl = _transcode_url(url)
            tdst = dst + '.mp3'
            ttmp = tdst + '.part'
            try:
                log('    falling back to the Commons MP3 transcode: %s' % turl)
                net.get(turl, to_file=ttmp, tries=3, deadline=deadline + 60.0, max_wait=60.0)
                pr = verify_audio(ttmp if ttmp.endswith('.mp3') else ttmp)
                want = float(ii.get('duration') or 0.0)
                if want and abs(pr['duration'] - want) > max(0.5, 0.02 * want):
                    raise ValueError('transcode lasts %.2f s, the original %.2f s' % (pr['duration'], want))
                os.replace(ttmp, tdst)
                got, variant = tdst, 'transcode-mp3'
            except (RuntimeError, ValueError) as e:
                why_q += '; the MP3 transcode failed too (%s)' % e
            finally:
                if os.path.exists(ttmp):
                    os.remove(ttmp)
        if got is None:
            queued.append(dict(title=title, path='wikimedia/' + rel, used_by=used, url=url,
                               file_page=ii.get('descriptionurl'), licence=lic_short, artist=g('Artist'),
                               bytes=ii.get('size'), reason=why_q or 'not downloaded'))
            continue
        try:
            probe = verify_audio(got)
        except ValueError as e:
            errors.append('wikimedia/%s: %s' % (rel, e))
            continue
        prel = os.path.relpath(got, lib)
        rec = dict(title=title, path=prel, file_page=ii.get('descriptionurl'), url=url, sha1=ii.get('sha1'),
                   bytes=ii.get('size'), mime=ii.get('mime'), licence=lic_short, licence_code=lic,
                   usage_terms=g('UsageTerms'), artist=g('Artist'), credit=g('Credit'),
                   description=g('ImageDescription')[:300], used_by=used, probe=probe, variant=variant)
        if variant != 'original':
            rec['transcode_url'] = _transcode_url(url)
            rec['note'] = ('Commons MP3 transcode of the original (same recording, same licence); the original '
                           '(sha1 %s) was rate-limited at fetch time' % ii.get('sha1'))
        wman[title] = rec
        man.add(prel, source='wikimedia', page=ii.get('descriptionurl'),
                url=rec.get('transcode_url', url), author=g('Artist'), title=title[5:],
                licence='%s (Wikimedia Commons)' % lic_short, credit=g('Credit'), variant=variant,
                original_url=url, original_sha1=ii.get('sha1'))
        _save_wman(wman, lib, mpath, queued)            # progress survives an interrupted run
        man.save()
    _save_wman(wman, lib, mpath, queued)
    return errors, queued


def _save_wman(wman, lib, mpath, queued=()):
    os.makedirs(os.path.dirname(mpath), exist_ok=True)
    keep = [wman[t] for t in sorted(wman) if os.path.isfile(os.path.join(lib, wman[t]['path']))]
    with open(mpath + '.part', 'w') as f:
        json.dump(dict(generator='pipeline/jawad_reels/tools/fetch_sfx_library.py', files=keep,
                       queued=sorted(queued, key=lambda q: q['path'])), f, indent=1)
    os.replace(mpath + '.part', mpath)


# ============================================================================================ LICENSES.md
def write_licenses(lib, files, queued=()):
    by = {}
    for e in files:
        by.setdefault(e.get('source', '?'), []).append(e)
    mb = lambda es: sum(e['bytes'] for e in es) / 1e6
    L = ['# CC0 / public-domain sample library (epic_sfx.py *_real sounds)', '',
         'Generated by `pipeline/jawad_reels/tools/fetch_sfx_library.py` (run it to rebuild the library; this file is '
         'rewritten from `library/manifest.json` on every run). Location: `workspace/brand_reels/sfx/library/` '
         '(git-ignored data). Only CC0 1.0 and public-domain files are accepted: the licence of every file was '
         'checked at download time (Kenney `License.txt`, the OpenGameArt licence field, the Wikimedia Commons '
         'extmetadata licence). No attribution is legally required for any file; the authors are credited here anyway.',
         '', 'Downloads are untrusted data: one folder per source, decoded only by ffmpeg / ffprobe (epic_sfx '
         '`_decode` -> `samples48/`), never executed.', '',
         '| source | files | MB | licence |', '|---|---|---|---|']
    for s in ('kenney', 'opengameart', 'wikimedia'):
        es = by.get(s, [])
        L.append('| %s | %d | %.1f | %s |' % (s, len(es), mb(es), {'kenney': 'CC0 1.0', 'opengameart': 'CC0',
                                                                     'wikimedia': 'CC0 / public domain'}[s]))
    L.append('| **total** | %d | %.1f | |' % (len(files), mb(files)))
    L += ['', '## Sounds that read these files', '',
          '| file | used by |', '|---|---|']
    for rel in sorted(USED_BY):
        L.append('| `%s` | %s |' % (rel, USED_BY[rel]))
    for title, rel, used in WIKIMEDIA:
        if not used.startswith('('):
            L.append('| `wikimedia/%s` (or its Commons MP3 transcode `wikimedia/%s.mp3`) | %s |' % (rel, rel, used))
    L += ['', 'A `*_real` sound registers only when its file is present (epic_sfx.register()); the reel modules read '
          '`%s` directly.' % '` and `'.join(REEL_PATHS), '']
    if queued:
        L += ['## QUEUED: not downloaded yet (optional; rerun the fetcher later)', '',
              'These CC0 / public-domain Commons files are part of the kit but were not fetched on the last run '
              '(upload.wikimedia.org rate-limits shared IPs with HTTP 429 pages and `Retry-After: 600`). The sounds that '
              'need them simply do not register until they are present. Rerun '
              '`python3 -I pipeline/jawad_reels/tools/fetch_sfx_library.py --only wikimedia` later.', '',
              '| file | Commons page | licence | author | used by | why queued |', '|---|---|---|---|---|---|']
        for q in sorted(queued, key=lambda q: q['path']):
            L.append('| `%s` | %s | %s | %s | %s | %s |' % (
                q['path'], q.get('file_page') or 'https://commons.wikimedia.org/wiki/' + q['title'].replace(' ', '_'),
                q.get('licence') or '(CC0 / PD per sound_design.md section 2; re-checked at download)',
                q.get('artist') or '?', q.get('used_by', ''), q.get('reason', '')))
        L.append('')
    L += ['## Kenney (www.kenney.nl), CC0 1.0', '']
    for pack, count, _ in KENNEY:
        es = sorted([e for e in by.get('kenney', []) if e.get('pack') == pack], key=lambda e: e['path'])
        if not es:
            L += ['### %s: NOT PRESENT (run the fetcher)' % pack, '']
            continue
        L += ['### %s' % pack, '', '- page: %s' % es[0]['page'], '- download: %s' % es[0]['url'],
              '- author: Kenney (www.kenney.nl); licence: CC0 1.0 (License.txt in the pack)',
              '- %d files, %.2f MB' % (len(es), mb(es)), '', '| file | bytes | sha256 |', '|---|---|---|']
        for e in es:
            L.append('| `%s` | %d | %s |' % (e['path'], e['bytes'], e['sha256'][:16]))
        L.append('')
    L += ['## OpenGameArt.org (CC0)', '']
    for item in OPENGAMEART:
        es = sorted([e for e in by.get('opengameart', []) if e.get('item') == item['key']], key=lambda e: e['path'])
        L += ['### %s: "%s" by %s' % (item['key'], item['title'], item['author']), '', '- page: %s' % item['page']]
        if not es:
            L += ['- NOT PRESENT (run the fetcher)', '']
            continue
        L += ['- licence: %s' % es[0]['licence'], '- %d file(s), %.2f MB' % (len(es), mb(es)), '',
              '| file | download | bytes | sha256 |', '|---|---|---|---|']
        for e in es:
            L.append('| `%s` | %s%s | %d | %s |' % (e['path'], e['url'], (' (from %s)' % e['archive'])
                                                      if e.get('archive') else '', e['bytes'], e['sha256'][:16]))
        L.append('')
    L += ['## Wikimedia Commons (CC0 / public domain)', '', '| file | Commons page | author | licence | source / credit '
          '| bytes | sha256 |', '|---|---|---|---|---|---|---|']
    for e in sorted(by.get('wikimedia', []), key=lambda e: e['path']):
        note = (' (Commons MP3 transcode of the original, sha1 %s; same recording, same licence)'
                % (e.get('original_sha1') or '?')) if e.get('variant') == 'transcode-mp3' else ''
        L.append('| `%s` | %s | %s | %s | %s%s | %d | %s |' % (e['path'], e.get('page'), e.get('author') or '?',
                                                              e.get('licence'), (e.get('credit') or '')[:160], note,
                                                              e['bytes'], e['sha256'][:16]))
    L += ['', 'Machine-readable records: `library/manifest.json` (every file) and `library/wikimedia/manifest.json` '
          '(the Commons metadata, incl. sha1 and the original URL).', '']
    txt = '\n'.join(L)
    p = os.path.join(lib, 'LICENSES.md')
    with open(p + '.part', 'w') as f:
        f.write(txt)
    os.replace(p + '.part', p)
    return p, txt


def kit_links(lib):
    """<library>/../epic_*.py -> ../../../pipeline/jawad_reels/epic_*.py (relative symlinks; regular files untouched)."""
    sfxdir = os.path.dirname(os.path.abspath(lib))
    made = []
    for m in KIT_MODULES:
        link = os.path.join(sfxdir, m)
        target = os.path.relpath(os.path.join(PIPE, m), sfxdir)
        if os.path.islink(link):
            if os.readlink(link) == target:
                continue
            os.remove(link)
        elif os.path.exists(link):
            continue
        os.symlink(target, link)
        made.append('%s -> %s' % (link, target))
    return made


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--lib', default=os.environ.get('EPIC_SFX_LIB') or DEFAULT_LIB)
    ap.add_argument('--only', default='kenney,opengameart,wikimedia')
    ap.add_argument('--extras', action='store_true', help='also the queued Commons extras (Tick2, rain 42 MB)')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--dry-run', action='store_true', help='list what would be fetched, download nothing')
    ap.add_argument('--no-copy', action='store_true', help='do not copy LICENSES.md to pipeline/jawad_reels')
    ap.add_argument('--no-kit-links', action='store_true')
    ap.add_argument('--wm-budget', type=float, default=240.0,
                    help='seconds the Wikimedia stage may spend in all (rate-limit back-offs included); default 240')
    ap.add_argument('--no-transcode', action='store_true',
                    help='never fall back to the Commons MP3 transcode when an original stays rate-limited')
    a = ap.parse_args(argv)
    lib = os.path.abspath(a.lib)
    only = set(x.strip() for x in a.only.split(',') if x.strip())
    if a.dry_run:
        for pack, count, url in KENNEY:
            print('kenney/%s  (%d files)  %s' % (pack, count, url))
        for it in OPENGAMEART:
            print('opengameart/%s  %s  %s' % (it['key'], it['page'], [f for f, _ in it['files']]))
        for t, rel, used in WIKIMEDIA + (WIKIMEDIA_EXTRAS if a.extras else []):
            print('wikimedia/%s  <- %s  (%s)' % (rel, t, used))
        return 0
    os.makedirs(lib, exist_ok=True)
    t0 = time.time()
    net = Net()
    man = Manifest(lib)
    errors = []
    log('library: %s' % lib)
    if 'kenney' in only:
        errors += fetch_kenney(net, man, lib, a.force)
        man.save()
    if 'opengameart' in only:
        errors += fetch_opengameart(net, man, lib, a.force)
        man.save()
    queued = []
    if 'wikimedia' in only:
        er, queued = fetch_wikimedia(net, man, lib, a.extras, a.force, a.wm_budget, not a.no_transcode)
        errors += er
    else:
        try:
            with open(os.path.join(lib, 'wikimedia', 'manifest.json')) as f:
                queued = json.load(f).get('queued', [])
        except Exception:
            queued = []
    files = man.save()
    p, txt = write_licenses(lib, files, queued)
    if not a.no_copy:
        with open(LICENSE_COPY + '.part', 'w') as f:
            f.write(txt)
        os.replace(LICENSE_COPY + '.part', LICENSE_COPY)
    links = [] if a.no_kit_links else kit_links(lib)
    need = (['opengameart/%s/%s' % (it['key'], loc) for it in OPENGAMEART for _, loc in it['files'] if loc] +
            list(REEL_PATHS) + sorted(USED_BY))
    missing = sorted(set(r for r in need if not os.path.isfile(os.path.join(lib, r))))
    have = lambda rel: os.path.isfile(os.path.join(lib, rel)) or os.path.isfile(os.path.join(lib, rel + '.mp3'))
    optional = [('wikimedia/' + rel) for _, rel, _ in WIKIMEDIA if not have('wikimedia/' + rel)]
    nbytes = sum(e['bytes'] for e in files)
    log('')
    log('files: %d (%.1f MB) | audio: %d | requests: %d | %.0f s' % (
        len(files), nbytes / 1e6, sum(e['path'].endswith(AUDIO_EXT) for e in files), net.requests, time.time() - t0))
    log('licences: %s%s' % (p, '' if a.no_copy else ' (copy: %s)' % LICENSE_COPY))
    for m in links:
        log('kit link: %s' % m)
    for q in queued:
        log('QUEUED (optional): %s (%s)' % (q['path'], q.get('reason', '')))
    for r in optional:
        if r not in [q['path'] for q in queued]:
            log('NOT PRESENT (optional): %s' % r)
    for e in errors:
        log('ERROR: %s' % e)
    for r in missing:
        log('MISSING (required): %s' % r)
    return 1 if (errors or missing) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
