function openPopup() {
        document.getElementById("popup").style.display = "flex";
        document.querySelector(".table").classList.add("blur");
        document.querySelector(".main").classList.add("blur");
      }

      function closePopup() {
        document.getElementById("popup").style.display = "none";
        document.querySelector(".table").classList.remove("blur");
        document.querySelector(".main").classList.remove("blur");
      }

      function saveTask() {
        let task = document.getElementById("taskName").value;
        let project = document.getElementById("projectName").value;
        let priority = document.getElementById("priority").value;
        let date = document.getElementById("dueDate").value;
        let time = document.getElementById("dueTime").value;

        if (!task || !project || !date || !time) {
          alert("Please fill all fields");
          return;
        }

        let table = document.querySelector("table");
        let row = document.createElement("tr");
        row.setAttribute("data-date", date);
        row.setAttribute("data-time", time);

        let priorityClass =
          priority === "High"
            ? "priority-high"
            : priority === "Medium"
            ? "priority-med"
            : "priority-low";

        row.innerHTML = `
          <td>${task}</td>
          <td>${project}</td>
          <td class="${priorityClass}">${priority}</td>
          <td>${date}</td>
          <td>${time}</td>
          <td><button class="complete-btn" onclick="markComplete(this)">✔ Complete</button></td>
        `;

        table.appendChild(row);
        closePopup();
      }

      function markComplete(button) {
        let row = button.parentElement.parentElement;
        row.classList.add("completed");
        button.style.display = "none";

        let count = document.getElementById("completed-count");
        count.innerText = Number(count.innerText) + 1;
      }

      function checkDeadlines() {
        const now = new Date();
        const rows = document.querySelectorAll("tr[data-date]");
        let alertMessage = "";
        let alertType = "";

        rows.forEach((row) => {
          const due = new Date(row.dataset.date + " " + row.dataset.time);
          const diffMs = due - now;
          const diffHours = diffMs / (1000 * 60 * 60);
          const diffDays = Math.floor(diffHours / 24);

          if (diffMs < 0) {
            alertMessage = " Some tasks are OVERDUE (time passed)!";
            alertType = "alert-danger";
          } else if (diffHours <= 1) {
            alertMessage = " A task is due within 1 hour!";
            alertType = "alert-warning";
          } else if (diffDays === 0) {
            alertMessage = "You have tasks due TODAY!";
            alertType = "alert-warning";
          } else if (diffDays === 1) {
            alertMessage = " Tasks due TOMORROW.";
            alertType = "alert-info";
          }
        });

        if (alertMessage) {
          const alertBar = document.getElementById("alert-bar");
          alertBar.innerHTML = alertMessage;
          alertBar.classList.add(alertType);
          alertBar.style.display = "block";
        }
      }

      checkDeadlines();