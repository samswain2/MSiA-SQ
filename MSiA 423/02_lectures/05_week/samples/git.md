# Git Branching

#### Create local git repository
    git init
    git add README.md
    git commit -m "first commit"
    git branch -M main
    git remote add origin https://github.com/pujari/test.git
    git push -u origin main

####  List branches
    git branch

####  Work in a branch
    git branch feature1
    git checkout <branch>

####  Make changes
    git add .
    git commit -m "new changes added"

#### Push changes
    git push -u origin <branch>
    git push --all -u

#### Merging branch with main
    git fetch
    git rebase origin/master
    git checkout master
    git pull origin master
    git merge <branch>
    git push origin master
