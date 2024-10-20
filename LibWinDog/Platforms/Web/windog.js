window.inputFrameResize = (function(height){
	var frameEl = document.querySelector('.input-frame');
	var frameWindow = frameEl.querySelector('iframe').contentWindow;
	var textEl = frameWindow.document.querySelector('form > [name="text"]');
	textEl.style.minHeight = 0;
	frameEl.style.height = '1em';
	//if (textEl.scrollHeight > frameWindow.document.documentElement.clientHeight) {
	if (textEl.scrollHeight / parseInt(getComputedStyle(textEl).height.slice(0, -2)) < 5) {
		frameEl.style.height = ('calc(3em + ' + (textEl.scrollHeight + 4) + 'px)');
		frameEl.dataset.scrollHeightOld = textEl.scrollHeight;
	} else {
		frameEl.style.height = ('calc(3em + ' + (parseInt(frameEl.dataset.scrollHeightOld) + 4) + 'px)');
	}
	textEl.style.minHeight = null;
/*	if (!frameEl.dataset.height) {
		frameEl.dataset.height = 0;
	}
	if (frameEl.dataset.height > )
	frameEl.style.height = ('calc(4em + ' + height + 'px)');
	frameEl.dataset.height = height;
*/
});
if (document.documentElement.className.split(' ').includes('form')) {
	var intervalFocus = setInterval(function(){
		try {
			document.querySelector('form > [name="text"]').focus();
			clearInterval(intervalFocus);
		} catch(err) {}
	}, 100);
}
