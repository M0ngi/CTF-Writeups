$(document).ready(function() {
	// update input label on selection
	$('#imageFile').change(function() {
		readURL(this);
	});
	setRGB();
	$('#colorPicker').change(setRGB);
});

const setRGB = () => {
	hexV = $('#colorPicker').val();
	window.rgb = hex2rgb(hexV);
}

const hex2rgb = (hex) => {
	return ['0x' + hex[1] + hex[2] | 0, '0x' + hex[3] + hex[4] | 0, '0x' + hex[5] + hex[6] | 0];
}


const readURL = (input) => {
	$('.resp').hide();
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = (e) => {
			if (!e.target.result.includes('data:image')) {
				$('.resp').show();
				return;
			}
            $('#uploadPreview').attr('src', e.target.result);
			encoded = e.target.result.toString().replace(/^data:(.*,)?/, '');
			if ((encoded.length % 4) > 0) {
				encoded += '='.repeat(4 - (encoded.length % 4));
			}
			upload(encoded);
        }
		reader.onerror = () => {
			$('.resp').show();
		}
        reader.readAsDataURL(input.files[0]);
    }
}

const upload = async (imageFile) => {
	$('#imageFile').prop('disabled', true);
	$('#loading-container').show();
	$('#progressbar').css({
		'width': '0%',
		'transition': 'none'
	});
	setTimeout(() => {
		$('#progressbar').css({
			'width': '100%',
			'transition': '10s'
		});
	}, 100);
	await new Promise(r => setTimeout(r, 1000));
	await fetch('/api/alphafy', {
			method: 'POST',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({image: imageFile, background: window.rgb}),
		})
		.then((response) => response.json()
			.then((resp) => {
				$('#loading-container').hide();
				if (resp.hasOwnProperty('image')) {
					$('#outputPreview').attr('src', resp.image);
					$('#imageFile').prop('disabled', false);
					return;
				}
				$('.resp').show();
			}))
		.catch((error) => {
			$('#loading-container').hide();
			$('.resp').show();
		});

	$('#imageFile').prop('disabled', false);
}

function update(e){
	var x = e.clientX || e.touches[0].clientX
	var y = e.clientY || e.touches[0].clientY
  
	document.documentElement.style.setProperty('--cursorX', x + 'px')
	document.documentElement.style.setProperty('--cursorY', y + 'px')
  }
  
  document.addEventListener('mousemove',update)
  document.addEventListener('touchmove',update)