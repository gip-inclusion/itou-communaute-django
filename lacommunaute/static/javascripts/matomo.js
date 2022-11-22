/********************************************************************
     Send an event to Matomo on click.
    Usage:
    <a href="#" class="matomo-event" data-matomo-category="MyCategory"
    data-matomo-action="MyAction" data-matomo-option="MyOption" >
********************************************************************/
document.addEventListener("matomo_loaded", (e) => {
    if (window._paq !== undefined) {
        $(".matomo-event").on("click", function () {
            var category = $(this).data("matomo-category");
            var action = $(this).data("matomo-action");
            var option = $(this).data("matomo-option");
            window._paq.push(['trackEvent', category, action, option]);
        });
    }
}, false);
