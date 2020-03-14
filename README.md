## Setup

1. Install Python 3.8
2. Install virtualenv: `pip install virtualenv`
3. `cd` to the project root directory
4. Create virtualenv: `virtualenv --python=YOUR_PYTHON_3.8_PATH venv`
5. Activate virtualenv: `source venv/bin/activate`
6. `pip install -r requirements.txt`
7. Configure git (you can add `--global` if you would like to set this for your
entire systems, not just this repo):
    ```
    git config user.name "Your Name"
    git config user.email "your@email"
    git config pull.rebase true
    git config branch.autosetuprebase always
    ```
8. Setup your editor. For PyCharm, configure the project interpreter in 
    File -> Settings -> Project -> Project Interpreter. Add a new interpreter
    from the existing virtualenv in ./venv (the Python interpreter path should
    end with venv/bin/python).

## Devel process

Create your branch

```
git branch yourbranch
git checkout yourbranch
```

Make some changes and commit

```
git add new_file.txt
git commit -m "meaningful changes..."
```

See if the app works locally

```
python app.py
```

If it runs, change to staging and merge in your changes.

```
git checkout staging
git merge yourbranch
git push orign staging
```

See if the page works (here)[http://coronus-staging.herokuapp.com/].
If it does, make a pull request to production on (github)[https://github.com/mandrecki/coronus/compare/production...staging?expand=1].
You want to merge into *production*, but first you want others to see your code and changes to the app. Describe your changes briefly and tag relevant coders.




