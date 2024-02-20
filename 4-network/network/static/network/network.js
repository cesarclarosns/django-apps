document.addEventListener("DOMContentLoaded", () => {
  // Use buttons to load different views
  document
    .querySelector("#btn-compose-form")
    .addEventListener("click", () => composePost());
  document
    .querySelector("#load-posts")
    .addEventListener("click", () => loadPosts("all"));
  document
    .querySelector("#load-posts-following")
    .addEventListener("click", () => loadPosts("following"));
  document
    .querySelector("#load-user-profile")
    .addEventListener("click", () => loadProfile(id));

  // Load all posts by default
  loadPosts("all");
});

function composePost() {
  // Get form content
  const content = document.querySelector("#compose-content").value;

  // Create new post
  fetch("/post/create", {
    method: "POST",
    body: JSON.stringify({
      content: content,
    }),
  })
    .then((response) => response.json())
    .then((result) => {
      console.log(result);
      // Load all posts
      loadPosts("all");
    });
}

function createPostComponent(post) {
  // Create new post component
  let div_post = document.createElement("div");
  div_post.classList.add("card");
  let div_body = document.createElement("div");
  div_body.classList.add("card-body");

  let a_profile = document.createElement("a");
  a_profile.classList.add("username");
  a_profile.innerHTML = `${post.poster_username}`;
  a_profile.addEventListener("click", () => loadProfile(post.poster_id));
  div_body.append(a_profile);

  if (id === post.poster_id) {
    // Create a button to let the user edit the post
    let div_edit = document.createElement("div");
    let a_edit = document.createElement("a");
    a_edit.classList.add("a-edit");
    a_edit.innerHTML = "Edit";
    a_edit.addEventListener("click", () => {
      // Hide other views
      document.querySelector("#profile-view").style.display = "none";
      document.querySelector("#compose-post-view").style.display = "none";
      document.querySelector("#posts-view").style.display = "none";

      // Pre-fill the form with the post's content
      document.querySelector("#edit-content").value = post.content;
      // Add eventListener to edit the post.
      document
        .querySelector("#btn-edit-form")
        .addEventListener("click", () => editPost(post));

      // Display the form to edit the post
      document.querySelector("#edit-post-view").style.display = "block";
    });
    div_edit.append(a_edit);
    div_body.append(div_edit);
  }

  let div_content = document.createElement("div");
  div_content.classList.add("disabled");
  div_content.innerHTML = `<div>${post.content}</div><div class="text-muted">${post.timestamp}</div>`;
  div_body.append(div_content);

  let a_react = document.createElement("a");
  a_react.innerHTML = post.reacted.includes(username)
    ? `<i class="fas fa-heart"><span class="mx-2">${post.reacted.length}</span></i>`
    : `<i class="far fa-heart"><span class="mx-2">${post.reacted.length}</span></i>`;
  a_react.addEventListener("click", (event) => {
    reactToPost(post, event.currentTarget);
  });
  div_body.append(a_react);

  div_post.append(div_body);

  return div_post;
}

function editPost(post) {
  // Get form content
  const content = document.querySelector("#edit-content").value;
  fetch(`/post/edit/${post.id}`, {
    method: "PUT",
    body: JSON.stringify({
      content: content,
    }),
  })
    .then((response) => response.json())
    .then((result) => {
      console.log(result);
      loadPosts("all");
    });
}

function followUser(user, button_follow, div_metrics) {
  if (user.followers.includes(username)) {
    fetch(`/profile/${user.id}/unfollow`, { method: "PUT" })
      .then((response) => response.json())
      .then((result) => {
        console.log(result);
        updateProfile(user.id, button_follow, div_metrics);
      });
  } else {
    fetch(`/profile/${user.id}/follow`, { method: "PUT" })
      .then((response) => response.json())
      .then((result) => {
        console.log(result);
        updateProfile(user.id, button_follow, div_metrics);
      });
  }
}

function loadPosts(type) {
  // Hide and show corresponding views
  document.querySelector("#profile-view").style.display = "none";
  document.querySelector("#compose-content").value = "";
  document.querySelector("#compose-post-view").style.display = "block";
  document.querySelector("#edit-post-view").style.display = "none";

  // Load posts
  const posts_view = document.querySelector("#posts-view");
  posts_view.innerHTML = "";
  posts_view.style.display = "block";

  fetch(`/posts/${type}`)
    .then((response) => response.json())
    .then((posts) => {
      // Implement paginator using PaginationJS library
      paginator(posts, posts_view, type);
    });
}

function loadProfile(user_id) {
  // Hide and show corresponding views
  id !== user_id
    ? (document.querySelector("#compose-post-view").style.display = "none")
    : (document.querySelector("#compose-post-view").style.display = "block");
  document.querySelector("#edit-post-view").style.display = "none";

  const posts_view = document.querySelector("#posts-view");
  posts_view.innerHTML = "";
  const profile_view = document.querySelector("#profile-view");
  profile_view.classList.add("text-center");
  profile_view.innerHTML = "";

  // Load data
  fetch(`/posts/${user_id}`)
    .then((response) => response.json())
    .then((user) => {
      console.log(user);
      // Load profile data
      const div_header = document.createElement("div");
      div_header.classList.add("m-1");
      div_header.innerHTML = `<div class="username">${user.username}</div>`;
      profile_view.append(div_header);

      const div_metrics = document.createElement("div");
      div_metrics.classList.add("m-1");
      div_metrics.innerHTML = `
        <span class="mx-1">
          ${user.followers.length}<span class="mx-1 text-muted">Followers</span>
        </span>
        <span class="mx-1">
          ${user.following.length}<span class="mx-1 text-muted">Following</span>
        </span>`;

      if (user_id !== id) {
        const button_follow = document.createElement("button");
        button_follow.classList.add("btn", "btn-dark", "m-1");
        button_follow.innerHTML = user.followers.includes(username)
          ? "Unfollow"
          : "Follow";
        button_follow.addEventListener("click", () => {
          followUser(user, button_follow, div_metrics);
        });
        profile_view.append(button_follow);
      }

      profile_view.append(div_metrics);

      // Load posts
      user.posts.forEach((post) => {
        let div_post = createPostComponent(post);
        posts_view.append(div_post);
      });
    });

  profile_view.style.display = "block";
}

function paginator(posts, posts_view, type) {
  // PaginationJS
  $("#paginator").pagination({
    dataSource: posts,
    pageSize: 10,
    showPageNumbers: false,
    showNavigator: false,
    activeClassName: "page-item",
    disableClassName: "page-item disabled",
    ulClassName: "pagination justify-content-center",

    callback: function (data, pagination) {
      // Load posts to posts_view
      $("#posts-view").html("");
      data.forEach((post) => {
        let div_post = createPostComponent(post);
        posts_view.append(div_post);
      });
      // Update posts
      fetch(`/posts/${type}`)
        .then((response) => response.json())
        .then((posts) => {
          this.dataSource = posts;
        });
    },
  });
}

function reactToPost(post, a_react) {
  post.reacted.includes(username)
    ? fetch(`/post/${post.id}/unlike`, { method: "PUT" }).then((response) =>
        response.json().then((result) => {
          console.log(result);
          updatePost(post.id, a_react);
        })
      )
    : fetch(`/post/${post.id}/like`, { method: "PUT" }).then((response) =>
        response.json().then((result) => {
          console.log(result);
          updatePost(post.id, a_react);
        })
      );
}

function updateProfile(user_id, button_follow, div_metrics) {
  // Update button_follow and div_metrics
  fetch(`/posts/${user_id}`)
    .then((response) => response.json())
    .then((user) => {
      console.log(user);
      const div_new_metrics = document.createElement("div");
      div_new_metrics.classList.add("m-1");
      div_new_metrics.innerHTML = `
        <span class="mx-1">
          ${user.followers.length}<span class="mx-1 text-muted">Followers</span>
        </span>
        <span class="mx-1">
          ${user.following.length}<span class="mx-1 text-muted">Following</span>
        </span>`;

      const button_new_follow = document.createElement("button");
      button_new_follow.classList.add("m-1");
      button_new_follow.classList.add("btn", "btn-dark");
      button_new_follow.innerHTML = user.followers.includes(username)
        ? "Unfollow"
        : "Follow";
      button_new_follow.addEventListener("click", () => {
        followUser(user, button_new_follow, div_new_metrics);
      });
      button_follow.replaceWith(button_new_follow);
      div_metrics.replaceWith(div_new_metrics);
    });
}

function updatePost(post_id, a_react_prev) {
  fetch(`/post/${post_id}`)
    .then((response) => response.json())
    .then((post) => {
      let a_react = document.createElement("a");
      a_react.innerHTML = post.reacted.includes(username)
        ? `<i class="fas fa-heart"><span class="mx-2">${post.reacted.length}</span></i>`
        : `<i class="far fa-heart"><span class="mx-2">${post.reacted.length}</span></i>`;
      a_react.addEventListener("click", (event) => {
        reactToPost(post, event.currentTarget);
      });
      // Update a_react_prev
      a_react_prev.replaceWith(a_react);
    });
}
