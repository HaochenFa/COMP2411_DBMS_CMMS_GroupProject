document.addEventListener("DOMContentLoaded", () => {
  console.log("CMMS App Initialized");

  // Highlight active sidebar link based on current URL
  const currentPath = window.location.pathname.split("/").pop() || "index.html";
  const navLinks = document.querySelectorAll(".nav-link");

  navLinks.forEach((link) => {
    const href = link.getAttribute("href");
    if (href === currentPath) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });

  // Mock function to simulate fetching data
  // In real app, this would be fetch('/api/persons')
  window.fetchData = async (endpoint) => {
    console.log(`Fetching data from ${endpoint}...`);
    // Return mock data for now
    return { status: "success", data: [] };
  };
});
