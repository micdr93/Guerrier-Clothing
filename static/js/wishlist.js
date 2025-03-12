document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".wishlist-toggle").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            let productId = this.dataset.productId;
            let actionUrl = this.dataset.action;
            let isInWishlist = this.classList.contains("in-wishlist");

            fetch(actionUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({}),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.classList.toggle("in-wishlist");
                        this.innerHTML = data.in_wishlist
                            ? '<i class="fa-solid fa-heart text-black"></i>'
                            : '<i class="fa-regular fa-heart"></i>';
                    }
                })
                .catch(error => console.error("Error:", error));
        });
    });
});

function getCSRFToken() {
    let csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
    return csrfToken ? csrfToken.value : "";
}
