# Open the Social Studio with Claude Code

Paste the prompt below into Claude Code (the Code tab of the Claude desktop app, or `claude` in a terminal) on the computer and account you want to run the studio from. It sets the studio up, signs Claude Code in to the Claude plan if needed, starts the server and opens the studio.

The studio runs on the Claude plan signed in to Claude Code on that computer (no API key, no Anthropic Console account). Research counts towards that plan's usage limits.

---

```text
Set up and open the Bespoke Bathroom UK Social Studio on this computer, running on my Claude plan. No API key and no Anthropic Console account.

1. The code is in github.com/jawad150/100 on branch claude/festive-lovelace-6gletw, folder bespoke_bathroom/. If a checkout already exists on this computer (for example C:\Users\JD\Desktop\remote\100), fetch and check out that branch there. Otherwise clone it with large files skipped (set GIT_LFS_SKIP_SMUDGE=1 and use a blobless clone, --filter=blob:none), because the repo holds gigabytes of videos the studio does not need.
2. Before doing anything else, read bespoke_bathroom/README.md, bespoke_bathroom/data/brand.json, bespoke_bathroom/data/strategy.json and .claude/agents/bespoke-bathroom-social.md.
3. In bespoke_bathroom, run npm install.
4. Check Claude Code's sign-in with the binary the Agent SDK ships: node_modules/@anthropic-ai/claude-agent-sdk-<platform>-<arch>/claude.exe auth status (claude without .exe on Mac or Linux). It must show "loggedIn": true, "authMethod": "claude.ai" and the email of the Claude account I use for the studio. If it does not, run that same binary with auth login --claudeai in a terminal tab I can see, tell me to sign in with my Claude account, and wait until I say I am done, then check again. Never enter a sign-in code or password for me.
5. Start the studio in a terminal tab so it keeps running after this session: node server.js in bespoke_bathroom. Then open http://localhost:4321 in my browser and confirm Settings shows the Claude plan as signed in.
6. Follow the writing rules in the agent file: British English, no em-dashes, never invent reviews or stats.
```
