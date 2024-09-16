// Existing code for slides
let slideIndex = 0;
showSlides();

function showSlides() {
  let slides = document.getElementsByClassName("slides");
  for (let i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
  slideIndex++;
  if (slideIndex > slides.length) {
    slideIndex = 1;
  }
  slides[slideIndex - 1].style.display = "block";
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
