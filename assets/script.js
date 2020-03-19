function scrollToContent() {
        const contentTop = document.getElementById('page-content').offsetTop;
        window.scroll({top: contentTop, left: 0, behavior: 'smooth'});
    }

$(document).ready(function() {
    $(document).on('click', '.menu a', scrollToContent)

});