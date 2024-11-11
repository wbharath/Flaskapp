// Existing code for slides
let slideIndex = 0;
showSlides();

function showSlides() {
  let slides = document.getElementsByClassName("slides");

  // Hide all slides initially
  for (let i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }

  // Increment slide index
  slideIndex++;

  // If we go past the last slide, reset to the first slide
  if (slideIndex > slides.length) {
    slideIndex = 1;
  }

  // Display the current slide
  slides[slideIndex - 1].style.display = "block";

  // Set up the next transition
  setTimeout(showSlides, 3000); // Change image every 3 seconds
}

function openContactForm() {
  console.log("Opening contact form");
  document.getElementById("contactFormPopup").style.display = "flex";
}

function closeContactForm() {
  console.log("Closing contact form");
  document.getElementById("contactFormPopup").style.display = "none";
  window.location.href = "/home"; // Redirect to index.html
}

// Open contact form when the page loads
if (window.location.pathname === "/contact") {
  openContactForm();
}
