# RestResource #

RestResource is a cherrypy controller mixin to make it easy to build REST applications.

It handles nested resources and method-based dispatching.

Here's a rough sample of what a controller would look like using this:

```
cherrypy.root = MainController()
cherrypy.root.user = UserController()

class PostController(RESTResource):
    def read(self,post):
        return post.as_html()
    read.expose_resource = True

    def delete(self,post):
        post.destroySelf()
        return "ok"
    delete.expose_resource = True

    def update(self,post,title="",body=""):
        post.title = title
        post.body = body
        return "ok"
    update.expose_resource = True

    def create(self, post, title="", body="")
        post.title = title
        post.body = body
        return "ok"
    create.expose_resource = True

    def REST_instantiate(self, slug, **kwargs):
        try:
            user = self.parents[0]
            return Post.select(Post.q.slug == slug, Post.q.userID = user.id)[0]
        except:
            return None

    def REST_create(self, slug, **kwargs):
        user = self.parents[0]
        return Post(slug=slug,user=user)

class UserController(RESTResource):
    REST_children = {'posts' : PostController()}

    def read(self,user):
        return user.as_html()
    read.expose_resource = True

    def delete(self,user):
        user.destroySelf()
        return "ok"
    delete.expose_resource = True

    def update(self,user,fullname="",email=""):
        user.fullname = fullname
        user.email = email
        return "ok"
    update.expose_resource = True

    def create(self, user, fullname="", email=""):
        user.fullname = fullname
        user.email = email
        return "ok"
    create.expose_resource = True

    def extra_action(self,user):
        # do something else
    extra_action.expose_resource = True

    def REST_instantiate(self, username, **kwargs):
        try:
            return User.byUsername(username)
        except:
            return None

    def REST_create(self, username, **kwargs):
        return User(username=username)

```

Then, the site would have urls like:

```
    /user/bob
    /user/bob/posts/my-first-post
    /user/bob/posts/my-second-post
    /user/bob/extra_action
```

Which represent REST resources. Calling 'GET /usr/bob' would call the read() method on UserController
for the user bob. 'PUT /usr/joe' would create a new user with username 'joe'. 'DELETE /usr/joe'
would delete that user. 'GET /usr/bob/posts/my-first-post' would call read() on the Post Controller
with the post with the slug 'my-first-post' that is owned by bob.