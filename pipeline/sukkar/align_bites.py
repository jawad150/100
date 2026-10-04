"""Force-align the stretches of interview audio that contain the reel's lines.

Writes tx/aligned.json: {bite: [(WORD, start_s, end_s, score), ...]} in source-file seconds.
The text includes a few neighbouring words so each window is anchored on both sides.
"""
import json

import align

V = "src/C8950 V2 (1).mp4"   # vertical interview export (better audio)
C = "src/C8951.MP4"          # raw camera clip, voice-over only

JOBS = {
    "b1": (V, 63.2, 73.25, "and a little scary but it was really neat to see the cornea restore someone's sight "
                           "and i helped be a part of that so that was very gratifying"),
    "b2": (V, 383.55, 398.4, "i think you know i think the craft of plastic surgery it's boundless you're always "
                             "getting better and it takes literally years and years of training and experience and operating"),
    "b3": (V, 436.0, 453.7, "like myself they're still learning and their learning curve is a lot more steep because "
                            "i already maybe went through that a long time ago but we're always still learning and "
                            "chasing perfection and just you know at the end of the day knowing that you did a good "
                            "job and you feel really good about it"),
    "b56": (C, 167.75, 178.5, "it's a very challenging thing to do that actually i'd like to say that going to surgery "
                              "is like a spa day for me because when i'm in surgery i'm in control and and"),
    "b4": (C, 282.4, 304.3, "was so much fun to build and challenging at the same time but i think what we've created "
                            "here is a wonderful experience not only for the patient but for the staff that work here "
                            "as well as now the other doctors who are coming and using the facility which they love "
                            "for their patients because it's a lot better than environment for what we"),
}

if __name__ == "__main__":
    res = {k: align.align(*job) for k, job in JOBS.items()}
    json.dump({k: [list(x) for x in v] for k, v in res.items()}, open("tx/aligned.json", "w"), indent=0)
    for k, v in res.items():
        print(k, " ".join(w.lower() for w, *_ in v))
