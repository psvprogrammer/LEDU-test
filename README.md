# LEDU test task

admin access: admin/admin

# Task description

Test project 1:
Star ratings for projects/creators.
Create simple django project with following features:
- registration for users
- form/page for registered users to add new projects (project fields: title, user, description).
- index page with top rated projects list in the center and top rated users in sidebar
- optimize index page load with caching
- for each project entry in list ability (for both registered and anonymous users) to set rating in stars from 1 to 5
- set rating feature should works without page reload
- check that anonymous user can't set ratting several times
- on index page sort projects list and users list by overall rating
- sorting order should be selectable (high/low rating)
- give each user 15 tokens on registration and withdraw 1 token for 1 vote on project, if 0 tokens, user can't vote projects, show a popup.