// app/static/js/script.js
document.addEventListener("DOMContentLoaded", function() {
    const pages = document.querySelectorAll("#viewer img");
    if (!pages.length) return; // if no pages, do nothing

    let pageUrls = [];
    const pageImage = document.getElementById("pageImage");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const pageCounter = document.getElementById("pageCounter");

    // Assume the server rendered a global JS variable with pages if available
    // For simplicity, we parse the page URLs from a data attribute or hidden element.
    // Here, we assume the page URLs are embedded in a JSON script tag.
    try {
        pageUrls = JSON.parse(document.getElementById("pageData").textContent);
    } catch (error) {
        // Fallback: if no pageData element exists, try to extract from the image src.
        if (pageImage && pageImage.src) {
            pageUrls = [pageImage.src];
        }
    }

    let currentPage = 0;
    const updatePage = () => {
        pageImage.src = pageUrls[currentPage];
        pageCounter.textContent = `Page ${currentPage + 1} of ${pageUrls.length}`;
        prevBtn.disabled = (currentPage === 0);
        nextBtn.disabled = (currentPage === pageUrls.length - 1);
    };

    if (prevBtn && nextBtn) {
        prevBtn.addEventListener("click", () => {
            if (currentPage > 0) {
                currentPage--;
                updatePage();
            }
        });
        nextBtn.addEventListener("click", () => {
            if (currentPage < pageUrls.length - 1) {
                currentPage++;
                updatePage();
            }
        });
    }
});
