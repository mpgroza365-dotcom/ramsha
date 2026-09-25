function toggleMenu() {
    const menu = document.getElementById("sideMenu");
    const overlay = document.getElementById("overlay");

    if (menu) {
        menu.classList.toggle("open");
    }

    if (overlay) {
        overlay.classList.toggle("show");
    }
}


async function addToCart(id, button) {
    try {

        const response = await fetch(`/cart/add/${id}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });

        const data = await response.json();

        if (!data.success) {
            alert(data.message || "حدث خطأ أثناء إضافة المنتج");
            return;
        }

        updateCartCount(data.cart_count);

        showCartMessage("✅ تمت إضافة المنتج إلى سلة المشتريات");

        if (button) {

            const oldText = button.textContent;

            button.textContent = "✓";
            button.style.transform = "scale(1.1)";

            setTimeout(function () {

                button.textContent = oldText;
                button.style.transform = "";

            }, 600);
        }

    } catch (error) {

        console.error("Cart error:", error);

        alert("تعذر الاتصال بالسلة");
    }
}



function showCartMessage(message) {
    let toast = document.getElementById("cartToast");

    if (!toast) {
        toast = document.createElement("div");
        toast.id = "cartToast";

        toast.innerHTML = `
            <div style="
                width:34px;
                height:34px;
                min-width:34px;
                border-radius:50%;
                background:#e8f8ee;
                color:#168a45;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:19px;
                font-weight:900;
            ">✓</div>

            <div style="
                display:flex;
                flex-direction:column;
                gap:3px;
                text-align:right;
            ">
                <strong style="
                    color:#222;
                    font-size:14px;
                    font-weight:800;
                ">تمت الإضافة بنجاح</strong>

                <span style="
                    color:#777;
                    font-size:12px;
                    font-weight:500;
                ">تمت إضافة المنتج إلى سلة المشتريات</span>
            </div>
        `;

        toast.style.position = "fixed";
        toast.style.top = "76px";
        toast.style.right = "16px";
        toast.style.left = "16px";
        toast.style.maxWidth = "390px";
        toast.style.margin = "0 auto";
        toast.style.boxSizing = "border-box";
        toast.style.display = "flex";
        toast.style.alignItems = "center";
        toast.style.gap = "12px";
        toast.style.padding = "12px 14px";
        toast.style.background = "#ffffff";
        toast.style.borderRadius = "16px";
        toast.style.border = "1px solid #eeeeee";
        toast.style.boxShadow = "0 10px 30px rgba(0,0,0,0.12)";
        toast.style.zIndex = "99999";
        toast.style.direction = "rtl";
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-18px) scale(0.97)";
        toast.style.transition = "all 0.3s cubic-bezier(.2,.8,.2,1)";
        toast.style.pointerEvents = "none";

        document.body.appendChild(toast);
    }

    clearTimeout(window.cartToastTimer);

    toast.style.opacity = "1";
    toast.style.transform = "translateY(0) scale(1)";

    window.cartToastTimer = setTimeout(function () {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-18px) scale(0.97)";
    }, 2200);
}

function updateCartCount(count) {

    const topCount =
        document.getElementById("cartCount");

    const bottomCount =
        document.getElementById("bottomCartCount");


    if (topCount) {
        topCount.textContent = count;
    }

    if (bottomCount) {
        bottomCount.textContent = count;
    }
}


const searchInput =
    document.getElementById("searchInput");


if (searchInput) {

    searchInput.addEventListener("input", function () {

        const value =
            this.value.toLowerCase().trim();


        document
            .querySelectorAll(".product-card")
            .forEach(function (card) {

                const name =
                    card.dataset.name.toLowerCase();

                card.style.display =
                    name.includes(value)
                        ? ""
                        : "none";

            });
    });
}


function filterCategory(category, button) {

    document
        .querySelectorAll(".category")
        .forEach(function (item) {

            item.classList.remove("active");

        });


    if (button) {
        button.classList.add("active");
    }


    document
        .querySelectorAll(".product-card")
        .forEach(function (card) {

            if (category === "الكل") {

                card.style.display = "";

                return;
            }


            card.style.display =
                card.dataset.category === category
                    ? ""
                    : "none";

        });
}
