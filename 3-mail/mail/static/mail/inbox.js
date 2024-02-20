document.addEventListener("DOMContentLoaded", function () {
  // Use buttons to toggle between views
  document
    .querySelector("#inbox")
    .addEventListener("click", () => load_mailbox("inbox"));
  document
    .querySelector("#sent")
    .addEventListener("click", () => load_mailbox("sent"));
  document
    .querySelector("#archived")
    .addEventListener("click", () => load_mailbox("archive"));
  document.querySelector("#compose").addEventListener("click", compose_email);

  // Use button to post email
  document.querySelector("form").addEventListener("submit", send_email);

  // By default, load the inbox
  load_mailbox("inbox");
});

function archive_email(id, archive = true) {
  // Archive email
  fetch(`/emails/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      archived: archive,
    }),
  }).then(() => {
    // Load inbox
    load_mailbox("inbox", undefined);
  });
}

function compose_email(error_message = "none", email = null) {
  // Show compose view and hide other views
  document.querySelector("#email-view").style.display = "none";
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "block";
  // Show or hide status message
  document.querySelector("#status").style.display = error_message;

  // Clear out composition fields or pre-fill input tags
  document.querySelector("#compose-recipients").value =
    email !== null ? email.sender : "";
  document.querySelector("#compose-subject").value =
    email !== null
      ? email.subject.includes("Re: ")
        ? email.subject
        : "Re: " + email.subject
      : "";

  let body =
    email !== null
      ? `On ${email.timestamp} ${email.sender} wrote: ${email.body} `
      : "";
  document.querySelector("#compose-body").value = body;
}

function load_email(id, is_sent) {
  document.querySelector("#email-view").style.display = "block";
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "none";
  document.querySelector("#status").style.display = "none";

  document.querySelector("#email-view").innerHTML = "";

  // Request email using GET
  fetch(`/emails/${id}`)
    .then((response) => response.json())
    .then((email) => {
      let a_reply = '<a href="#" class="m-2" id="reply">Reply</a>';
      let a_archive = '<a href="#" class="m-2" id="archive">Archive</a';
      let a_unarchive = '<a href="#" class="m-2" id="unarchive">Unarchive</a';

      document.querySelector("#email-view").innerHTML = `
        <div class="text-muted">Subject: ${email.subject}</div>
        <div class="text-muted">From: ${email.sender}</div>
        <div class="text-muted">To: ${email.recipients.toString()}</div>
        <div class="text-muted">${email.timestamp}</div>
        <hr><div>${email.body}</div><hr>
        <div>
        ${
          // Add 'a' tags to reply, archive or unarchive an email
          is_sent === false && email.archived === false
            ? a_reply + "|" + a_archive
            : is_sent === false && email.archived === true
            ? a_reply + "|" + a_unarchive
            : a_reply
        }
        </div>`;

      // Add eventListener to the a tag with id "reply" to reply email
      document
        .getElementById("reply")
        .addEventListener("click", () => compose_email(undefined, email));
      // Add eventListener to the a tag with id "archive" or "unarchive"
      // to archive or unarchive email
      is_sent === false && email.archived === false
        ? document
            .getElementById("archive")
            .addEventListener("click", () => archive_email(email.id, undefined))
        : is_sent === false && email.archived === true
        ? document
            .getElementById("unarchive")
            .addEventListener("click", () => archive_email(email.id, false))
        : null;
    });

  // Mark email as read
  fetch(`/emails/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      read: true,
    }),
  });
}

function load_mailbox(mailbox, error_message = "none") {
  // Show the mailbox and hide other views
  document.querySelector("#email-view").style.display = "none";
  document.querySelector("#emails-view").style.display = "block";
  document.querySelector("#compose-view").style.display = "none";
  // Show or hide status message
  document.querySelector("#status").style.display = error_message;

  // Show the mailbox name
  document.querySelector("#emails-view").innerHTML = `
    <h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>
    <ul class="list-group" id="emails-list"></ul>`;

  // Clean emails
  document.querySelector("#emails-list").innerHTML = "";

  // Display specified emails
  fetch(`/emails/${mailbox}`)
    .then((response) => response.json())
    .then((emails) => {
      // ... do something else with emails ...
      emails.forEach((email) => {
        // Create li element
        const email_li = document.createElement("li");

        if (email.read === false) {
          email_li.classList.add("list-group-item");
        } else {
          email_li.classList.add(
            "list-group-item",
            "list-group-item-secondary"
          );
        }

        email_li.id = email.id;

        email_li.innerHTML =
          mailbox === "inbox" || mailbox === "archive"
            ? `
          <div class="ms-2 me-auto">
            <div class="fw-bold">From: ${email.sender}</div>
            <div>${email.subject}</div>
            <div class="text-muted">${email.timestamp}</div>
          </div>`
            : mailbox === "sent"
            ? `
          <div class="ms-2 me-auto">
            <div class="fw-bold">To: ${email.recipients.toString()}</div>
            <div>${email.subject}</div>
            <div class="text-muted">${email.timestamp}</div>
          </div>`
            : null;

        document.querySelector("#emails-list").append(email_li);
        // Add an event listener to the element
        let is_sent = mailbox === "sent" ? true : false;
        email_li.addEventListener("click", () => load_email(email.id, is_sent));
      });
    });
}

function send_email(event) {
  // Prevent the submit event
  event.preventDefault();

  // Get data from the form
  const recipients = document.querySelector("#compose-recipients").value;
  const subject = document.querySelector("#compose-subject").value;
  const body = document.querySelector("#compose-body").value;

  // Try to post email
  fetch("/emails", {
    method: "POST",
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body,
    }),
  })
    .then((response) => response.json())
    .then((result) => {
      // If the email wasn't sent, display a description of the error
      if (result.error) {
        document.querySelector("#error-message").innerHTML = `${result.error}`;
        compose_email(undefined, undefined);
      } else {
        load_mailbox("sent", undefined);
      }
    });
}
