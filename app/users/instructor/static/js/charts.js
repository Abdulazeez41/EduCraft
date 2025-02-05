document.addEventListener("DOMContentLoaded", function () {
  var ctx = document.getElementById("engagementChart").getContext("2d");

  var engagementChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Course A", "Course B", "Course C"],
      datasets: [
        {
          label: "Student Engagement",
          data: [75, 50, 90],
          backgroundColor: ["#007bff", "#28a745", "#ffc107"],
        },
      ],
    },
  });
});
