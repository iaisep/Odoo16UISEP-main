function download_as_pdf(e){
    const element = $('#custom_download_button')
    const name = element.data('slideName')
    const category = element.data('slideType')
    let url = new URL(document.URL);
    if(category == 'document'){
        url.pathname = url.pathname + "/pdf_content";
        downloadPDF(url.href, name)
        return
    }
    $('#custom_download_icon').hide();
    $('#custom_download_text').text("Descargando...");
    $('#custom_loading_spinner').show();
    const jsPdf = new window.jspdf.jsPDF({ unit: "mm", format : 'letter' })
    const htmlPdf = new window.html2pdf();
    let item = undefined;
    if(url.searchParams.has('fullscreen') && url.searchParams['fullscreen'] == 1){
        item = $('.o_wslides_fs_content').get(0);
    }else {
        const content = $('.o_wslides_lesson_content')
        item = document.createElement("div");
        let headers = content.children('.oe_structure')[0].cloneNode(true)
        let slides = $('.o_wslides_lesson_content_type > div > div > div')[0].cloneNode(true)

        if (headers.hasChildNodes()) {
          for (const node of headers.childNodes) {
            item.appendChild(node.cloneNode(true))
          }
        }

         if (slides.hasChildNodes()) {
          for (const node of slides.childNodes) {
            item.appendChild(node.cloneNode(true))
          }
        }
    }

        var opt = {
        pagebreak: { mode: 'avoid-all' },
  margin:       [12,12,12,12],
  filename:     name,
  image:        { type: 'jpeg', quality: 0.98 },
  html2canvas:  { scale: 1 },
  jsPDF:        { unit: 'mm', format: 'letter', orientation: 'portrait',
   width : 200.9, windowWidth : 720,
                autoPaging: 'text',
                margin: [72,72,72,72],
   }
};

// New Promise-based usage:
html2pdf().set(opt).from(item).save().then(() => {
                $('#custom_loading_spinner').hide();
                $('#custom_download_text').text("Descargar");
                $('#custom_download_icon').show();
});
}

async function downloadPDF(url, filename) {
  try {
	const response = await fetch(url);
	const blob = await response.blob();
	const link = document.createElement('a');
	link.href = URL.createObjectURL(blob);
	link.download = filename;
	document.body.appendChild(link);
	link.click();
	document.body.removeChild(link);
  } catch (error) {
	console.error('Error:', error);
  }
}

