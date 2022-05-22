const { Image } = require('image-js') 
module.exports = { 
	async addRedFilter(buffer) { 
		return new Promise(async (resolve, reject) => { 
			try { 
				image = await Image.load(buffer) 
				grey = image.grey(); 
				red = image.grey({algorithm:'red'}); 
				mask = red.mask(); 
				roiManager = image.getRoiManager(); 
				roiManager.fromMask(mask); 
				rois=roiManager.getRois({negative:false, minSurface:100}) 
				roisMasks=rois.map( (roi) => roi.mask); 
				result = grey.rgba8().paintMasks(roisMasks, {color:'red'}); 
				resolve(result.toDataURL()); 
			} catch(e) { 
				reject(e); 
			} 
		}); 
	} 
};
