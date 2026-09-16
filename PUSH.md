# Pushing this to a private GitHub repo

Everything that does not need your credentials is done:

    branch    main
    remote    origin -> https://github.com/trentenbryant746-del/atlas2.git
    commits   3, ready to push

No tooling to install. This machine has no Homebrew and no `gh`, and
neither is needed — git 2.39.5 is present and GitHub is reachable over
HTTPS.

## 1. Create the empty repo on github.com

New repository → name **atlas2** → **Private** → create.

Do NOT tick "Add a README", ".gitignore" or "licence". This repo already
has all three, and adding them creates a conflicting first commit.

If your username is not `trentenbryant746-del`:

    git remote set-url origin https://github.com/YOURNAME/atlas2.git

## 2. Make a token

github.com → Settings → Developer settings → Personal access tokens →
**Tokens (classic)** → Generate new token.

    scope     repo        (the only one needed)
    expiry    your call

Copy it. GitHub shows it once.

## 3. Push, from your own terminal

    cd ~/Documents/atlas2
    git push -u origin main

Git will ask for two things:

    Username: your GitHub username
    Password: PASTE THE TOKEN, not your account password

Your terminal will not echo the token as you paste. That is expected.

To avoid retyping it next time:

    git config --global credential.helper osxkeychain

and push once more — macOS stores it after that.

## Verify it worked

The repo should show 3 commits and be marked **Private**. Then, in a
scratch directory:

    git clone https://github.com/YOURNAME/atlas2.git
    cd atlas2
    python3 eval/audit.py          expect 21/21
    python3 eval/integration.py    expect PASS

Godot is not in the repo — it is 162.7 MB and GitHub refuses files over
100 MB. Fetch it with:

    python3 tools/get_godot.py

## Afterwards

    git add -A
    git commit -m "..."
    git push
