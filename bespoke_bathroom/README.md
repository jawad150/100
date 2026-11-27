# Bespoke Bathroom UK · Social Studio

A local web app that runs the brand's social media content desk. It researches what is trending on Instagram, TikTok, YouTube, Facebook and Pinterest, then turns it into reels, carousels, statics and pins written for Bespoke Bathroom UK, with full scripts, captions, hashtags, lead mechanics and a PDF you can download.

## Start it

1. Install Node.js (LTS) from nodejs.org, once.
2. Open this `bespoke_bathroom` folder.
3. Mac: double-click `start.command`. Windows: double-click `start.bat`. Linux: run `./start.sh`.
4. Your browser opens at http://localhost:4321.

To have Claude Code set everything up for you instead, paste the prompt in [OPEN-WITH-CLAUDE.md](OPEN-WITH-CLAUDE.md).

## First time only

The studio has no API key. It runs on the Claude plan (Pro, Max or higher) signed in to Claude Code on this computer, so research uses the plan's allowance, not API credits.

1. Install Claude Code, once, if it is not already installed (code.claude.com).
2. Open a terminal and run `claude auth login` (on Windows PowerShell, `claude.cmd auth login`). Your browser opens; sign in with the account that has your Claude plan, and paste the code back into the terminal if it asks.
3. Back in the studio, press **I've signed in**. Live research is now on.
4. In Settings (the gear icon), leave "Daily auto-research" on.

If research ever says Claude Code is not signed in, run the sign-in command again.

Use the studio on your own computer with your own plan. Anthropic does not allow claude.ai plan sign-in in tools offered to other people, so a team that shares the studio needs each person on their own plan, or an API key set-up instead.

## Every day

1. Open the studio. Today's research runs by itself the first time you open it each day.
2. Pick a focus: **Balanced**, **Lead Gen** (enquiries and 3D designs) or **Brand & Viral** (reach, shares, saves).
3. Switch platforms on or off. Switch on **Pinterest Lab** for static post and carousel ideas built from Pinterest trends.
4. Press **Research today** for a fresh run, or **Update · next 3 days** for a three-day plan.
5. Tap any idea for the script, slides, caption, hashtags and Pinterest moodboards. Use **Rework** to change it.
6. **Add to planner** to move ideas through Planned, Scripted, Shot, Scheduled and Posted.
7. Press **Download PDF** for the brief.

## Keep the agent sharp

- **Brand Brain:** fill in the [ADD] gaps (location, social handles, real reviews). Every research run reads it.
- **Learn from website and socials:** the agent reads the website and profiles and suggests updates for you to approve.
- **Strategy:** the plan the agent works inside. Download it as a PDF for the team.

## Good to know

- Everything is stored in the `data` folder on this computer. No key is stored by the studio: the sign-in lives with Claude Code.
- Runs count towards your Claude plan's usage limits, so briefs show "Claude plan" instead of a price. Settings lets you switch to Sonnet 5.5 for faster runs that use less of the allowance, or Deep research for more searches.
- The three "launch" briefs from 26 November 2026 were researched by hand from sourced trend reports so the studio has real content before the first live run.
