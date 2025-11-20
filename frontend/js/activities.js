document.addEventListener("DOMContentLoaded", async () => {
  // Load existing activities
  const activities = await api.get("/activities");
  if (activities)
    utils.renderTable("activitiesTableBody", activities, [
      "id",
      "name",
      "type",
      "date",
      "location_id",
    ]);

  const createBtn = document.querySelector(".btn-primary");
  if (createBtn) {
    createBtn.addEventListener("click", async () => {
      const contractor =
        document.querySelectorAll('input[type="text"]')[2].value;
      const name = document.querySelector(
        'input[placeholder*="Activity Name"]'
      ).value;
      const type = document.querySelector("select").value; // Ensure first select is Type
      const date = document.querySelector('input[type="date"]').value;
      const location = document.querySelectorAll("select")[1].value; // Ensure second select is Location
      const organizer = document.querySelector(
        'input[placeholder*="ID"]'
      ).value;

      if (name && date) {
        const result = await api.post("/activities", {
          name,
          type,
          date,
          location_id: location,
          organizer_id: organizer,
          contractor: contractor,
        });
        if (result) {
          alert("Activity Created");
          location.reload();
        }
      }
    });
  }
});
