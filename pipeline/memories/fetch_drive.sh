#!/bin/bash
# Re-download the user's Spider-Man asset packs from the shared Google Drive folder 'spiderman'
# (folder must be shared as "Anyone with the link") and unpack them to workspace2/assets/drive/x.
set -e
cd "$(dirname "$0")/../.."
D=workspace2/assets/drive
mkdir -p "$D/x"
dl() { id=$1; name=$2
  [ -d "$D/x/${name%.zip}" ] && return
  for i in 1 2 3 4; do
    curl -sSL --max-time 1800 -o "$D/$name" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t" && \
      file "$D/$name" | grep -q "Zip archive" && break
    sleep $((2 ** i))
  done
  mkdir -p "$D/x/${name%.zip}" && unzip -qo "$D/$name" -d "$D/x/${name%.zip}" && rm "$D/$name"
  for z in "$D/x/${name%.zip}"/source/*.zip; do
    [ -f "$z" ] && mkdir -p "$(dirname "$z")/unz" && unzip -qo "$z" -d "$(dirname "$z")/unz" && rm "$z"
  done
  echo "ok $name"
}
dl 1TxKv7RJ_4PoT0UdpH1dlzE_dLYJ2_Ohl mary-jane-spiderman.zip
dl 10aliIqee6kL4WtN31Sg_A9bmuqdTqk_m 2004-spiderman-sam-raimi.zip
dl 1ku6mFn1E-IccyUsvQVuMOwm3TY_d9jhf spiderman-green-goblin-pumpkin-bomb.zip
dl 1amom_j1pLPdeiobUEYvOACJ3YB19fSmA symbiote-spiderman-tobey-maguire.zip
dl 1sPJCr1b-3SV27HT9aMxReOss2OuARGQR miles-morales-spiderman-logo.zip
dl 1EVhDT8XherD7WA-yWUZTCu6aurAeQQXr a-memory.zip
dl 1TxKqEkWlLc9wVK280YA4vouXA6H8tFzB red-rose.zip
dl 1lNQGDUYD-WyNSIcnzpXOY992aZGPdkEC lasso-of-truth.zip
dl 1mp0LCtxOi0OWdL2FJvr3WvNQTH_aO482 gladius-one-truth-can-puncture-a-thousand-lies.zip
dl 1IT5VTCE0hX0QnKr6peWRouibDg6JSMJm landscape-forest-mountains.zip
dl 1AKS9Ozme6vMQ1lmMrOjAxzf_SXZkTkTP an-overgrown-japanese-style-location.zip
dl 1NQfYOGLwxlhUvDqT_H8ODGPnjT4U7cya obelisk-of-xulazar.zip
dl 1Dd0vflNhpEZWaFHyz8SpVfVBfFQG6ZCn dark-scene-diorama.zip
dl 1BbKQUiSkSCQbiqxddSAqka12NedD8eSI memory-bank.zip
dl 17ZuYRhWp5wyrRC3EzGx-6Y7UwEc0h1Pn major-general-f-f-minchin-1860-1922-cross.zip
dl 1OA5nKFY9IVW7g-sFJGtxQH2eCH93QFZZ green-goblin-2002.zip
dl 1t7XKYzGQvUQr5-4hI5lca3OlKFpYO-3p spiderman-logo.zip
dl 15--B6JE-DNPXvpkZ28gD1dd9yHTI-86h hw-xyz-damage-emotional.zip
dl 1B15ZSo68K00ofWd6ZmncRvoi5dLa9yG0 bottle.zip
# memory-bank ships as COLLADA (dropped in Blender 5): convert to glb
if [ ! -f "$D/x/memory-bank/source/memory_bank.glb" ]; then
  pip install -q pycollada trimesh
  python3 -c "import trimesh; trimesh.load('$D/x/memory-bank/source/unz/model/model.dae', force='scene').export('$D/x/memory-bank/source/memory_bank.glb')"
fi
