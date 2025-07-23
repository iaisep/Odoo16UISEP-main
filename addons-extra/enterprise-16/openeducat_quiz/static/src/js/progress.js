$(document).ready(function () {
    progress($('.progress-value').text(), $('#progressBar'));
    function progress(percent, $element) {
        var progressBarWidth = percent * $element.width() / 100;
        $element.find('div').animate({ width: progressBarWidth }, 1200).html(percent + "% ");
    }
});
