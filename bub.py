import os
from datetime import datetime
from markdown2 import markdown
import glob
from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader("bub"))

if not os.path.exists("public"):
    os.mkdir("public")

POSTS = {}
for f in glob.iglob("content/*.md"):
    base_name = os.path.basename(f)
    file_name = os.path.splitext(base_name)[0]
    destination = os.path.join("public", f"{file_name}.html")

    with open(f, "r") as file:
        raw = file.read()
        POSTS[file_name] = markdown(raw, extras=["metadata"])

POSTS = {
    post: POSTS[post]
    for post in sorted(
        POSTS,
        key=lambda post: datetime.strptime(POSTS[post].metadata["date"], "%Y-%m-%d"),
        reverse=True,
    )
}

home_template = env.get_template("home.html")
blog_template = env.get_template("blog.html")
post_template = env.get_template("post.html")

posts_metadata = [POSTS[post].metadata for post in POSTS]
tags = [post["tags"] for post in posts_metadata]
home_html = home_template.render()
blog_html = blog_template.render(posts=posts_metadata, tags=tags)
with open("public/index.html", "w") as file:
    file.write(home_html)

with open("public/blog.html", "w") as file:
    file.write(blog_html)

for post in POSTS:
    post_metadata = POSTS[post].metadata

    post_data = {
        "content": POSTS[post],
        "title": post_metadata["title"],
        "date": post_metadata["date"],
    }

    post_html = post_template.render(post=post_data)
    post_file_path = "public/posts/{slug}.html".format(slug=post_metadata["slug"])

    os.makedirs(os.path.dirname(post_file_path), exist_ok=True)
    with open(post_file_path, "w") as file:
        file.write(post_html)
