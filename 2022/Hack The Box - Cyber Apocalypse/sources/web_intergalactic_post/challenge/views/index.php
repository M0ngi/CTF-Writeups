<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>The Intergalactic Post</title>
        <link rel="icon" href="/static/images/logo.png" />
        <link rel="stylesheet" type="text/css" href="/static/css/main.css" />
    </head>
	<body>
	<div id="starfield"></div>
	<div id="app">
		<div class='gui'>
			<div class="ui-border-v2 t">
				<svg viewBox="0 0 620 30">
					<path d="M628.587,25.19l-7.963-13.811h-0.008L617.525,6.03A12.244,12.244,0,0,0,607.74.994H409.994V0h198.43c4.149,0,8.2,2.1,9.748,4.781l2.949,5.089h0.028l8.086,14.062A12.237,12.237,0,0,0,639.03,29h80.976v0.006h77.735a12.243,12.243,0,0,0,9.784-5.037l3.091-5.348h0.008l7.963-13.811C820.142,2.113,824.192,0,828.345,0H1029.99V1H829.029a12.237,12.237,0,0,0-9.794,5.068L811.15,20.131h-0.029l-2.948,5.089C806.618,27.9,802.573,30,798.424,30H638.345C634.192,30,630.142,27.887,628.587,25.19Z" transform="translate(-410)"></path>
				</svg>
				<div class="batt"></div>
			</div>
			<div class='ui-c-border' v-for='n in ["t", "b"]' :class='n' :key='n + Math.random() + "border"'>
				<svg viewBox="0 0 620 30">
					<path d="M628.587,25.19l-7.963-13.811h-0.008L617.525,6.03A12.244,12.244,0,0,0,607.74.994H409.994V0h198.43c4.149,0,8.2,2.1,9.748,4.781l2.949,5.089h0.028l8.086,14.062A12.237,12.237,0,0,0,639.03,29h80.976v0.006h77.735a12.243,12.243,0,0,0,9.784-5.037l3.091-5.348h0.008l7.963-13.811C820.142,2.113,824.192,0,828.345,0H1029.99V1H829.029a12.237,12.237,0,0,0-9.794,5.068L811.15,20.131h-0.029l-2.948,5.089C806.618,27.9,802.573,30,798.424,30H638.345C634.192,30,630.142,27.887,628.587,25.19Z" transform="translate(-410)"></path>
				</svg>
				<span class='batt'></span>
			</div>
			<div class='ui-border' v-for='n in ["l","r"]' :class='n' :key='"UIBorder" + n'>
				<i class='cap t'></i>
				<i class='batt'></i>
				<i class='cap b'></i>
			</div>
			<div class='ui-cross'>
				<div class='border-x f'></div>
				<div class='border-x l'></div>
				<div class='border-horz'></div>
				<div class='border-vert'>
					<div class='dot' v-for='n in ["t", "b"]' :class='n' :key='n + Math.random() + "dot"'>
						<div class='x-hair'>
							<div class='line' v-for='n in 4' :key='n * Math.random() + "line"'></div>
						</div>
					</div>
				</div>
			</div>
			<div class='ui-circles' v-for='n in ["l","r"]' :class='n' :key='"UICircles" + n'>
				<div class='circle' v-for='n in 6' :key='n * Math.random() + "circle"'></div>
			</div>
			<div class="ui-text r">
				<h5>SciFi Mission</h5>
				<div class="t-o">
					<svg viewBox="0 0 101 67">
						<path d="M767,453h-1v-1h4v1h-3Zm1-22h1v1h-1v-1Zm-7,0h5v1h-5v-1Zm-9,0h4v1h-4v-1Zm-7,0h5v1h-5v-1Zm-4,0h2v1h-2v-1Zm-3,0h2v1h-2v-1Zm-2,0h1v1h-1v-1Zm17,3H735v-1h18v1Zm-20-3h2v1h-2v-1Zm-15,0h14v1H718v-1Zm16,3H715v-1h19v1Zm-37-3h18v1H697v-1Zm17,3H694v-1h20v1Zm-29-1h7v1h-7v-1Zm-4-2h10v1H681v-1Zm-12,0h9v1h-9v-1Zm15,3H669v-1h15v1Zm0,2H669v-1h15v1Zm-4,2H669v-1h11v1Zm-9,2h-2v-1h2v1Zm5-1v1h-4v-1h4Zm2,3h-9v-1h9v1Zm-7,2h-2v-1h2v1Zm0,2h-2v-1h2v1Zm4,2h-6v-1h6v1Zm-2,2h-4v-1h4v1Zm3,2h-7v-1h7v1Zm23,2H669v-1h30v1Zm-28,2h-2v-1h2v1Zm3-1v1h-2v-1h2Zm4,0v1h-3v-1h3Zm5,0v1h-4v-1h4Zm10,0v1h-8v-1h8Zm4,0v1h-3v-1h3Zm20,3H669v-1h48v1Zm-32,2H669v-1h16v1Zm-13,2h-3v-1h3v1Zm5-1v1h-4v-1h4Zm5,0v1h-2v-1h2Zm4,1v-1h4v1h-4Zm0-3h9v1h-9v-1Zm12,0v1h-1v-1h1Zm3,0v1h-1v-1h1Zm4,0v1h-2v-1h2Zm4,0v1h-3v-1h3Zm0,5H669v-1h40v1Zm-34,2h-6v-1h6v1Zm-5,32h-1v-1h1v1Zm45-18H671v-1h44v1Zm-38,18h-5v-1h5v1Zm9,0h-4v-1h4v1Zm7,0h-5v-1h5v1Zm4,0h-2v-1h2v1Zm3,0h-2v-1h2v1Zm2,0h-1v-1h1v1Zm-10-13v1h-2v-1h2Zm-7,10h18v1H685v-1Zm20,3h-2v-1h2v1Zm15,0H706v-1h14v1Zm-16-3h19v1H704v-1Zm37,3H723v-1h18v1Zm-17-3h20v1H724v-1Zm29,1h-7v-1h7v1Zm4,2H747v-1h10v1Zm12-2H754v-1h15v1Zm0-2H754v-1h15v1Zm0-2H758v-1h11v1Zm0-2h-2v-1h2v1Zm-7,0v-1h4v1h-4Zm7-2h-9v-1h9v1Zm0-2h-2v-1h2v1Zm0-2h-2v-1h2v1Zm0-2h-6v-1h6v1Zm0-2h-4v-1h4v1Zm0-2h-7v-1h7v1Zm0-2H739v-1h30v1Zm0-2h-2v-1h2v1Zm-5,0v-1h2v1h-2Zm-4,0v-1h3v1h-3Zm-5,0v-1h4v1h-4Zm-10,0v-1h8v1h-8Zm-4,0v-1h3v1h-3Zm28-2H721v-1h48v1Zm0-2H753v-1h16v1Zm0-2h-3v-1h3v1Zm-8,0v-1h4v1h-4Zm-5,0v-1h2v1h-2Zm-4-1v1h-4v-1h4Zm0,3h-9v-1h9v1Zm-12,0v-1h1v1h-1Zm-3,0v-1h1v1h-1Zm-4,0v-1h2v1h-2Zm-4,0v-1h3v1h-3Zm40-4H729v-1h40v1Zm0-2h-6v-1h6v1Zm-25-20H731v-1h13v1Zm-12,2h-2v-1h2v1Zm-1-10h-2v-1h2v1Zm-2,2h-2v-1h2v1Zm0,2H716v-1h13v1Zm-6-2v-1h2v1h-2Zm-3,0v-1h2v1h-2Zm-3,0v-1h2v1h-2Zm10-2H715v-1h12v1Zm-11,2H701v-1h15v1Zm-4-2H696v-1h16v1Zm-23,11h3v1h-3v-1Zm1-6h3v1h-3v-1Zm3,3h-3v-1h3v1Zm5,11h4v1h-4v-1Zm3-11h-6v-1h6v1Zm-3-2h-4v-1h4v1Zm3-2h-3v-1h3v1Zm0,1h4v1h-4v-1Zm2-2h7v1h-7v-1Zm7,3h-3v-1h3v1Zm-7,1h10v1H703v-1Zm0,2h8v1h-8v-1Zm0,10h7v1h-7v-1Zm3-8h13v1H706v-1Zm5,8h6v1h-6v-1Zm15-9v-1h2v1h-2Zm-5,0v-1h2v1h-2Zm-2,0v-1h1v1h-1Zm-4,0v-1h2v1h-2Zm14-2H715v-1h14v1Zm-15,2h-2v-1h2v1Zm-1-7h2v1h-2v-1Zm8,3h-7v-1h7v1Zm-4,10h15v1H717v-1Zm6,4h-5v-1h5v1Zm-2,1v1h-3v-1h3Zm2,0h6v1h-6v-1Zm10,3H715v-1h18v1Zm-17,4h-2v-1h2v1Zm6,1h2v1h-2v-1Zm33-5h-3v-1h3v1Zm-20,0v-1h15v1H735Zm-4-3h23v1H731v-1Zm27,2v1h-2v-1h2Zm-41,4h45v1H717v-1Zm10,2h1v1h-1v-1Zm-2,4h2v1h-2v-1Zm-5,2v1h-3v-1h3Zm-5,2h5v1h-5v-1Zm2,11h-2v-1h2v1Zm-8,7h2v1h-2v-1Zm0-2h13v1H709v-1Zm6,2v1h-2v-1h2Zm3,0v1h-2v-1h2Zm3,0v1h-2v-1h2Zm-10,2h12v1H711v-1Zm11-2h15v1H722v-1Zm4,2h16v1H726v-1Zm15-4h12v1H741v-1Zm7,4h4v1h-4v-1Zm2-2h7v1h-7v-1Zm10-1h-3v-1h3v1Zm-6-2v-1h5v1h-5Zm-1,0h-4v-1h4v1Zm-3-3h10v1H750v-1Zm12-3h-2v-1h2v1Zm-9-1h2v1h-2v-1Zm3,0h2v1h-2v-1Zm-7,3v-1h8v1h-8Zm-31-1h1v1h-1v-1Zm8,1h-2v-1h2v1Zm-9,3h7v1h-7v-1Zm6,2h2v1h-2v-1Zm4-5v-1h8v1h-8Zm-2,1h10v1H725v-1Zm3,2h3v1h-3v-1Zm0,2h7v1h-7v-1Zm5-2h4v1h-4v-1Zm4-2h6v1h-6v-1Zm0,4h3v1h-3v-1Zm3-2h4v1h-4v-1Zm0-6h4v1h-4v-1Zm0,3h-4v-1h12v1h-8Zm5,1h3v1h-3v-1Zm1-4h3v1h-3v-1Zm-1,6h3v1h-3v-1Zm-24-3v-1h2v1h-2Zm-2-3h13v1H719v-1Zm8-8v1h-6v-1h6Zm8,0v1h-7v-1h7Zm5,1h-4v-1h4v1Zm22,6H719v-1h43v1Zm4,6h-5v-1h5v1Zm-8-3h6v1h-6v-1Zm-15,11v-1h4v1h-4Zm-2-3h7v1h-7v-1Zm-32,3h-2v-1h2v1Zm-2-8H694v-1h13v1Zm1-2h-2v-1h2v1Zm4-1v1h-2v-1h2Zm11,3H709v-1h14v1Zm-8-14h-6v-1h6v1Zm-10-3h18v1H705v-1Zm-2,1H688v-1h15v1Zm-23,0v-1h5v1h-5Zm41-4H676v-1h45v1Zm-10-2h-1v-1h1v1Zm2-4h-2v-1h2v1Zm-15-12h-4v-1h4v1Zm-8-2v-1h12v1H690Zm7-6H685v-1h12v1Zm-7-4h-4v-1h4v1Zm-2,2h-7v-1h7v1Zm-10,1h3v1h-3v-1Zm6,2v1h-5v-1h5Zm1,0h4v1h-4v-1Zm-5,6h2v1h-2v-1Zm5,1h-2v-1h2v1Zm-4-3h8v1h-8v-1Zm7-1H678v-1h10v1Zm-12,4v-1h2v1h-2Zm-4-5h5v1h-5v-1Zm8,3h-6v-1h6v1Zm15-11v1h-4v-1h4Zm2,3h-7v-1h7v1Zm51,5v1h-2v-1h2Zm16,10H736v-1h28v1Zm5,45h-9v-1h9v1Z" transform="translate(-669 -431)"></path>
					</svg>
					<svg viewBox="0 0 101 67">
						<path d="M767,453h-1v-1h4v1h-3Zm1-22h1v1h-1v-1Zm-7,0h5v1h-5v-1Zm-9,0h4v1h-4v-1Zm-7,0h5v1h-5v-1Zm-4,0h2v1h-2v-1Zm-3,0h2v1h-2v-1Zm-2,0h1v1h-1v-1Zm17,3H735v-1h18v1Zm-20-3h2v1h-2v-1Zm-15,0h14v1H718v-1Zm16,3H715v-1h19v1Zm-37-3h18v1H697v-1Zm17,3H694v-1h20v1Zm-29-1h7v1h-7v-1Zm-4-2h10v1H681v-1Zm-12,0h9v1h-9v-1Zm15,3H669v-1h15v1Zm0,2H669v-1h15v1Zm-4,2H669v-1h11v1Zm-9,2h-2v-1h2v1Zm5-1v1h-4v-1h4Zm2,3h-9v-1h9v1Zm-7,2h-2v-1h2v1Zm0,2h-2v-1h2v1Zm4,2h-6v-1h6v1Zm-2,2h-4v-1h4v1Zm3,2h-7v-1h7v1Zm23,2H669v-1h30v1Zm-28,2h-2v-1h2v1Zm3-1v1h-2v-1h2Zm4,0v1h-3v-1h3Zm5,0v1h-4v-1h4Zm10,0v1h-8v-1h8Zm4,0v1h-3v-1h3Zm20,3H669v-1h48v1Zm-32,2H669v-1h16v1Zm-13,2h-3v-1h3v1Zm5-1v1h-4v-1h4Zm5,0v1h-2v-1h2Zm4,1v-1h4v1h-4Zm0-3h9v1h-9v-1Zm12,0v1h-1v-1h1Zm3,0v1h-1v-1h1Zm4,0v1h-2v-1h2Zm4,0v1h-3v-1h3Zm0,5H669v-1h40v1Zm-34,2h-6v-1h6v1Zm-5,32h-1v-1h1v1Zm45-18H671v-1h44v1Zm-38,18h-5v-1h5v1Zm9,0h-4v-1h4v1Zm7,0h-5v-1h5v1Zm4,0h-2v-1h2v1Zm3,0h-2v-1h2v1Zm2,0h-1v-1h1v1Zm-10-13v1h-2v-1h2Zm-7,10h18v1H685v-1Zm20,3h-2v-1h2v1Zm15,0H706v-1h14v1Zm-16-3h19v1H704v-1Zm37,3H723v-1h18v1Zm-17-3h20v1H724v-1Zm29,1h-7v-1h7v1Zm4,2H747v-1h10v1Zm12-2H754v-1h15v1Zm0-2H754v-1h15v1Zm0-2H758v-1h11v1Zm0-2h-2v-1h2v1Zm-7,0v-1h4v1h-4Zm7-2h-9v-1h9v1Zm0-2h-2v-1h2v1Zm0-2h-2v-1h2v1Zm0-2h-6v-1h6v1Zm0-2h-4v-1h4v1Zm0-2h-7v-1h7v1Zm0-2H739v-1h30v1Zm0-2h-2v-1h2v1Zm-5,0v-1h2v1h-2Zm-4,0v-1h3v1h-3Zm-5,0v-1h4v1h-4Zm-10,0v-1h8v1h-8Zm-4,0v-1h3v1h-3Zm28-2H721v-1h48v1Zm0-2H753v-1h16v1Zm0-2h-3v-1h3v1Zm-8,0v-1h4v1h-4Zm-5,0v-1h2v1h-2Zm-4-1v1h-4v-1h4Zm0,3h-9v-1h9v1Zm-12,0v-1h1v1h-1Zm-3,0v-1h1v1h-1Zm-4,0v-1h2v1h-2Zm-4,0v-1h3v1h-3Zm40-4H729v-1h40v1Zm0-2h-6v-1h6v1Zm-25-20H731v-1h13v1Zm-12,2h-2v-1h2v1Zm-1-10h-2v-1h2v1Zm-2,2h-2v-1h2v1Zm0,2H716v-1h13v1Zm-6-2v-1h2v1h-2Zm-3,0v-1h2v1h-2Zm-3,0v-1h2v1h-2Zm10-2H715v-1h12v1Zm-11,2H701v-1h15v1Zm-4-2H696v-1h16v1Zm-23,11h3v1h-3v-1Zm1-6h3v1h-3v-1Zm3,3h-3v-1h3v1Zm5,11h4v1h-4v-1Zm3-11h-6v-1h6v1Zm-3-2h-4v-1h4v1Zm3-2h-3v-1h3v1Zm0,1h4v1h-4v-1Zm2-2h7v1h-7v-1Zm7,3h-3v-1h3v1Zm-7,1h10v1H703v-1Zm0,2h8v1h-8v-1Zm0,10h7v1h-7v-1Zm3-8h13v1H706v-1Zm5,8h6v1h-6v-1Zm15-9v-1h2v1h-2Zm-5,0v-1h2v1h-2Zm-2,0v-1h1v1h-1Zm-4,0v-1h2v1h-2Zm14-2H715v-1h14v1Zm-15,2h-2v-1h2v1Zm-1-7h2v1h-2v-1Zm8,3h-7v-1h7v1Zm-4,10h15v1H717v-1Zm6,4h-5v-1h5v1Zm-2,1v1h-3v-1h3Zm2,0h6v1h-6v-1Zm10,3H715v-1h18v1Zm-17,4h-2v-1h2v1Zm6,1h2v1h-2v-1Zm33-5h-3v-1h3v1Zm-20,0v-1h15v1H735Zm-4-3h23v1H731v-1Zm27,2v1h-2v-1h2Zm-41,4h45v1H717v-1Zm10,2h1v1h-1v-1Zm-2,4h2v1h-2v-1Zm-5,2v1h-3v-1h3Zm-5,2h5v1h-5v-1Zm2,11h-2v-1h2v1Zm-8,7h2v1h-2v-1Zm0-2h13v1H709v-1Zm6,2v1h-2v-1h2Zm3,0v1h-2v-1h2Zm3,0v1h-2v-1h2Zm-10,2h12v1H711v-1Zm11-2h15v1H722v-1Zm4,2h16v1H726v-1Zm15-4h12v1H741v-1Zm7,4h4v1h-4v-1Zm2-2h7v1h-7v-1Zm10-1h-3v-1h3v1Zm-6-2v-1h5v1h-5Zm-1,0h-4v-1h4v1Zm-3-3h10v1H750v-1Zm12-3h-2v-1h2v1Zm-9-1h2v1h-2v-1Zm3,0h2v1h-2v-1Zm-7,3v-1h8v1h-8Zm-31-1h1v1h-1v-1Zm8,1h-2v-1h2v1Zm-9,3h7v1h-7v-1Zm6,2h2v1h-2v-1Zm4-5v-1h8v1h-8Zm-2,1h10v1H725v-1Zm3,2h3v1h-3v-1Zm0,2h7v1h-7v-1Zm5-2h4v1h-4v-1Zm4-2h6v1h-6v-1Zm0,4h3v1h-3v-1Zm3-2h4v1h-4v-1Zm0-6h4v1h-4v-1Zm0,3h-4v-1h12v1h-8Zm5,1h3v1h-3v-1Zm1-4h3v1h-3v-1Zm-1,6h3v1h-3v-1Zm-24-3v-1h2v1h-2Zm-2-3h13v1H719v-1Zm8-8v1h-6v-1h6Zm8,0v1h-7v-1h7Zm5,1h-4v-1h4v1Zm22,6H719v-1h43v1Zm4,6h-5v-1h5v1Zm-8-3h6v1h-6v-1Zm-15,11v-1h4v1h-4Zm-2-3h7v1h-7v-1Zm-32,3h-2v-1h2v1Zm-2-8H694v-1h13v1Zm1-2h-2v-1h2v1Zm4-1v1h-2v-1h2Zm11,3H709v-1h14v1Zm-8-14h-6v-1h6v1Zm-10-3h18v1H705v-1Zm-2,1H688v-1h15v1Zm-23,0v-1h5v1h-5Zm41-4H676v-1h45v1Zm-10-2h-1v-1h1v1Zm2-4h-2v-1h2v1Zm-15-12h-4v-1h4v1Zm-8-2v-1h12v1H690Zm7-6H685v-1h12v1Zm-7-4h-4v-1h4v1Zm-2,2h-7v-1h7v1Zm-10,1h3v1h-3v-1Zm6,2v1h-5v-1h5Zm1,0h4v1h-4v-1Zm-5,6h2v1h-2v-1Zm5,1h-2v-1h2v1Zm-4-3h8v1h-8v-1Zm7-1H678v-1h10v1Zm-12,4v-1h2v1h-2Zm-4-5h5v1h-5v-1Zm8,3h-6v-1h6v1Zm15-11v1h-4v-1h4Zm2,3h-7v-1h7v1Zm51,5v1h-2v-1h2Zm16,10H736v-1h28v1Zm5,45h-9v-1h9v1Z" transform="translate(-669 -431)"></path>
					</svg>
				</div>
			</div>
			<div class="ui-text l">
				<h5>Space Domination</h5>
				<div class="t-o">
					<svg viewBox="0 0 101 67">
						<path d="M767,453h-1v-1h4v1h-3Zm1-22h1v1h-1v-1Zm-7,0h5v1h-5v-1Zm-9,0h4v1h-4v-1Zm-7,0h5v1h-5v-1Zm-4,0h2v1h-2v-1Zm-3,0h2v1h-2v-1Zm-2,0h1v1h-1v-1Zm17,3H735v-1h18v1Zm-20-3h2v1h-2v-1Zm-15,0h14v1H718v-1Zm16,3H715v-1h19v1Zm-37-3h18v1H697v-1Zm17,3H694v-1h20v1Zm-29-1h7v1h-7v-1Zm-4-2h10v1H681v-1Zm-12,0h9v1h-9v-1Zm15,3H669v-1h15v1Zm0,2H669v-1h15v1Zm-4,2H669v-1h11v1Zm-9,2h-2v-1h2v1Zm5-1v1h-4v-1h4Zm2,3h-9v-1h9v1Zm-7,2h-2v-1h2v1Zm0,2h-2v-1h2v1Zm4,2h-6v-1h6v1Zm-2,2h-4v-1h4v1Zm3,2h-7v-1h7v1Zm23,2H669v-1h30v1Zm-28,2h-2v-1h2v1Zm3-1v1h-2v-1h2Zm4,0v1h-3v-1h3Zm5,0v1h-4v-1h4Zm10,0v1h-8v-1h8Zm4,0v1h-3v-1h3Zm20,3H669v-1h48v1Zm-32,2H669v-1h16v1Zm-13,2h-3v-1h3v1Zm5-1v1h-4v-1h4Zm5,0v1h-2v-1h2Zm4,1v-1h4v1h-4Zm0-3h9v1h-9v-1Zm12,0v1h-1v-1h1Zm3,0v1h-1v-1h1Zm4,0v1h-2v-1h2Zm4,0v1h-3v-1h3Zm0,5H669v-1h40v1Zm-34,2h-6v-1h6v1Zm-5,32h-1v-1h1v1Zm45-18H671v-1h44v1Zm-38,18h-5v-1h5v1Zm9,0h-4v-1h4v1Zm7,0h-5v-1h5v1Zm4,0h-2v-1h2v1Zm3,0h-2v-1h2v1Zm2,0h-1v-1h1v1Zm-10-13v1h-2v-1h2Zm-7,10h18v1H685v-1Zm20,3h-2v-1h2v1Zm15,0H706v-1h14v1Zm-16-3h19v1H704v-1Zm37,3H723v-1h18v1Zm-17-3h20v1H724v-1Zm29,1h-7v-1h7v1Zm4,2H747v-1h10v1Zm12-2H754v-1h15v1Zm0-2H754v-1h15v1Zm0-2H758v-1h11v1Zm0-2h-2v-1h2v1Zm-7,0v-1h4v1h-4Zm7-2h-9v-1h9v1Zm0-2h-2v-1h2v1Zm0-2h-2v-1h2v1Zm0-2h-6v-1h6v1Zm0-2h-4v-1h4v1Zm0-2h-7v-1h7v1Zm0-2H739v-1h30v1Zm0-2h-2v-1h2v1Zm-5,0v-1h2v1h-2Zm-4,0v-1h3v1h-3Zm-5,0v-1h4v1h-4Zm-10,0v-1h8v1h-8Zm-4,0v-1h3v1h-3Zm28-2H721v-1h48v1Zm0-2H753v-1h16v1Zm0-2h-3v-1h3v1Zm-8,0v-1h4v1h-4Zm-5,0v-1h2v1h-2Zm-4-1v1h-4v-1h4Zm0,3h-9v-1h9v1Zm-12,0v-1h1v1h-1Zm-3,0v-1h1v1h-1Zm-4,0v-1h2v1h-2Zm-4,0v-1h3v1h-3Zm40-4H729v-1h40v1Zm0-2h-6v-1h6v1Zm-25-20H731v-1h13v1Zm-12,2h-2v-1h2v1Zm-1-10h-2v-1h2v1Zm-2,2h-2v-1h2v1Zm0,2H716v-1h13v1Zm-6-2v-1h2v1h-2Zm-3,0v-1h2v1h-2Zm-3,0v-1h2v1h-2Zm10-2H715v-1h12v1Zm-11,2H701v-1h15v1Zm-4-2H696v-1h16v1Zm-23,11h3v1h-3v-1Zm1-6h3v1h-3v-1Zm3,3h-3v-1h3v1Zm5,11h4v1h-4v-1Zm3-11h-6v-1h6v1Zm-3-2h-4v-1h4v1Zm3-2h-3v-1h3v1Zm0,1h4v1h-4v-1Zm2-2h7v1h-7v-1Zm7,3h-3v-1h3v1Zm-7,1h10v1H703v-1Zm0,2h8v1h-8v-1Zm0,10h7v1h-7v-1Zm3-8h13v1H706v-1Zm5,8h6v1h-6v-1Zm15-9v-1h2v1h-2Zm-5,0v-1h2v1h-2Zm-2,0v-1h1v1h-1Zm-4,0v-1h2v1h-2Zm14-2H715v-1h14v1Zm-15,2h-2v-1h2v1Zm-1-7h2v1h-2v-1Zm8,3h-7v-1h7v1Zm-4,10h15v1H717v-1Zm6,4h-5v-1h5v1Zm-2,1v1h-3v-1h3Zm2,0h6v1h-6v-1Zm10,3H715v-1h18v1Zm-17,4h-2v-1h2v1Zm6,1h2v1h-2v-1Zm33-5h-3v-1h3v1Zm-20,0v-1h15v1H735Zm-4-3h23v1H731v-1Zm27,2v1h-2v-1h2Zm-41,4h45v1H717v-1Zm10,2h1v1h-1v-1Zm-2,4h2v1h-2v-1Zm-5,2v1h-3v-1h3Zm-5,2h5v1h-5v-1Zm2,11h-2v-1h2v1Zm-8,7h2v1h-2v-1Zm0-2h13v1H709v-1Zm6,2v1h-2v-1h2Zm3,0v1h-2v-1h2Zm3,0v1h-2v-1h2Zm-10,2h12v1H711v-1Zm11-2h15v1H722v-1Zm4,2h16v1H726v-1Zm15-4h12v1H741v-1Zm7,4h4v1h-4v-1Zm2-2h7v1h-7v-1Zm10-1h-3v-1h3v1Zm-6-2v-1h5v1h-5Zm-1,0h-4v-1h4v1Zm-3-3h10v1H750v-1Zm12-3h-2v-1h2v1Zm-9-1h2v1h-2v-1Zm3,0h2v1h-2v-1Zm-7,3v-1h8v1h-8Zm-31-1h1v1h-1v-1Zm8,1h-2v-1h2v1Zm-9,3h7v1h-7v-1Zm6,2h2v1h-2v-1Zm4-5v-1h8v1h-8Zm-2,1h10v1H725v-1Zm3,2h3v1h-3v-1Zm0,2h7v1h-7v-1Zm5-2h4v1h-4v-1Zm4-2h6v1h-6v-1Zm0,4h3v1h-3v-1Zm3-2h4v1h-4v-1Zm0-6h4v1h-4v-1Zm0,3h-4v-1h12v1h-8Zm5,1h3v1h-3v-1Zm1-4h3v1h-3v-1Zm-1,6h3v1h-3v-1Zm-24-3v-1h2v1h-2Zm-2-3h13v1H719v-1Zm8-8v1h-6v-1h6Zm8,0v1h-7v-1h7Zm5,1h-4v-1h4v1Zm22,6H719v-1h43v1Zm4,6h-5v-1h5v1Zm-8-3h6v1h-6v-1Zm-15,11v-1h4v1h-4Zm-2-3h7v1h-7v-1Zm-32,3h-2v-1h2v1Zm-2-8H694v-1h13v1Zm1-2h-2v-1h2v1Zm4-1v1h-2v-1h2Zm11,3H709v-1h14v1Zm-8-14h-6v-1h6v1Zm-10-3h18v1H705v-1Zm-2,1H688v-1h15v1Zm-23,0v-1h5v1h-5Zm41-4H676v-1h45v1Zm-10-2h-1v-1h1v1Zm2-4h-2v-1h2v1Zm-15-12h-4v-1h4v1Zm-8-2v-1h12v1H690Zm7-6H685v-1h12v1Zm-7-4h-4v-1h4v1Zm-2,2h-7v-1h7v1Zm-10,1h3v1h-3v-1Zm6,2v1h-5v-1h5Zm1,0h4v1h-4v-1Zm-5,6h2v1h-2v-1Zm5,1h-2v-1h2v1Zm-4-3h8v1h-8v-1Zm7-1H678v-1h10v1Zm-12,4v-1h2v1h-2Zm-4-5h5v1h-5v-1Zm8,3h-6v-1h6v1Zm15-11v1h-4v-1h4Zm2,3h-7v-1h7v1Zm51,5v1h-2v-1h2Zm16,10H736v-1h28v1Zm5,45h-9v-1h9v1Z" transform="translate(-669 -431)"></path>
					</svg>
					<svg viewBox="0 0 101 67">
						<path d="M767,453h-1v-1h4v1h-3Zm1-22h1v1h-1v-1Zm-7,0h5v1h-5v-1Zm-9,0h4v1h-4v-1Zm-7,0h5v1h-5v-1Zm-4,0h2v1h-2v-1Zm-3,0h2v1h-2v-1Zm-2,0h1v1h-1v-1Zm17,3H735v-1h18v1Zm-20-3h2v1h-2v-1Zm-15,0h14v1H718v-1Zm16,3H715v-1h19v1Zm-37-3h18v1H697v-1Zm17,3H694v-1h20v1Zm-29-1h7v1h-7v-1Zm-4-2h10v1H681v-1Zm-12,0h9v1h-9v-1Zm15,3H669v-1h15v1Zm0,2H669v-1h15v1Zm-4,2H669v-1h11v1Zm-9,2h-2v-1h2v1Zm5-1v1h-4v-1h4Zm2,3h-9v-1h9v1Zm-7,2h-2v-1h2v1Zm0,2h-2v-1h2v1Zm4,2h-6v-1h6v1Zm-2,2h-4v-1h4v1Zm3,2h-7v-1h7v1Zm23,2H669v-1h30v1Zm-28,2h-2v-1h2v1Zm3-1v1h-2v-1h2Zm4,0v1h-3v-1h3Zm5,0v1h-4v-1h4Zm10,0v1h-8v-1h8Zm4,0v1h-3v-1h3Zm20,3H669v-1h48v1Zm-32,2H669v-1h16v1Zm-13,2h-3v-1h3v1Zm5-1v1h-4v-1h4Zm5,0v1h-2v-1h2Zm4,1v-1h4v1h-4Zm0-3h9v1h-9v-1Zm12,0v1h-1v-1h1Zm3,0v1h-1v-1h1Zm4,0v1h-2v-1h2Zm4,0v1h-3v-1h3Zm0,5H669v-1h40v1Zm-34,2h-6v-1h6v1Zm-5,32h-1v-1h1v1Zm45-18H671v-1h44v1Zm-38,18h-5v-1h5v1Zm9,0h-4v-1h4v1Zm7,0h-5v-1h5v1Zm4,0h-2v-1h2v1Zm3,0h-2v-1h2v1Zm2,0h-1v-1h1v1Zm-10-13v1h-2v-1h2Zm-7,10h18v1H685v-1Zm20,3h-2v-1h2v1Zm15,0H706v-1h14v1Zm-16-3h19v1H704v-1Zm37,3H723v-1h18v1Zm-17-3h20v1H724v-1Zm29,1h-7v-1h7v1Zm4,2H747v-1h10v1Zm12-2H754v-1h15v1Zm0-2H754v-1h15v1Zm0-2H758v-1h11v1Zm0-2h-2v-1h2v1Zm-7,0v-1h4v1h-4Zm7-2h-9v-1h9v1Zm0-2h-2v-1h2v1Zm0-2h-2v-1h2v1Zm0-2h-6v-1h6v1Zm0-2h-4v-1h4v1Zm0-2h-7v-1h7v1Zm0-2H739v-1h30v1Zm0-2h-2v-1h2v1Zm-5,0v-1h2v1h-2Zm-4,0v-1h3v1h-3Zm-5,0v-1h4v1h-4Zm-10,0v-1h8v1h-8Zm-4,0v-1h3v1h-3Zm28-2H721v-1h48v1Zm0-2H753v-1h16v1Zm0-2h-3v-1h3v1Zm-8,0v-1h4v1h-4Zm-5,0v-1h2v1h-2Zm-4-1v1h-4v-1h4Zm0,3h-9v-1h9v1Zm-12,0v-1h1v1h-1Zm-3,0v-1h1v1h-1Zm-4,0v-1h2v1h-2Zm-4,0v-1h3v1h-3Zm40-4H729v-1h40v1Zm0-2h-6v-1h6v1Zm-25-20H731v-1h13v1Zm-12,2h-2v-1h2v1Zm-1-10h-2v-1h2v1Zm-2,2h-2v-1h2v1Zm0,2H716v-1h13v1Zm-6-2v-1h2v1h-2Zm-3,0v-1h2v1h-2Zm-3,0v-1h2v1h-2Zm10-2H715v-1h12v1Zm-11,2H701v-1h15v1Zm-4-2H696v-1h16v1Zm-23,11h3v1h-3v-1Zm1-6h3v1h-3v-1Zm3,3h-3v-1h3v1Zm5,11h4v1h-4v-1Zm3-11h-6v-1h6v1Zm-3-2h-4v-1h4v1Zm3-2h-3v-1h3v1Zm0,1h4v1h-4v-1Zm2-2h7v1h-7v-1Zm7,3h-3v-1h3v1Zm-7,1h10v1H703v-1Zm0,2h8v1h-8v-1Zm0,10h7v1h-7v-1Zm3-8h13v1H706v-1Zm5,8h6v1h-6v-1Zm15-9v-1h2v1h-2Zm-5,0v-1h2v1h-2Zm-2,0v-1h1v1h-1Zm-4,0v-1h2v1h-2Zm14-2H715v-1h14v1Zm-15,2h-2v-1h2v1Zm-1-7h2v1h-2v-1Zm8,3h-7v-1h7v1Zm-4,10h15v1H717v-1Zm6,4h-5v-1h5v1Zm-2,1v1h-3v-1h3Zm2,0h6v1h-6v-1Zm10,3H715v-1h18v1Zm-17,4h-2v-1h2v1Zm6,1h2v1h-2v-1Zm33-5h-3v-1h3v1Zm-20,0v-1h15v1H735Zm-4-3h23v1H731v-1Zm27,2v1h-2v-1h2Zm-41,4h45v1H717v-1Zm10,2h1v1h-1v-1Zm-2,4h2v1h-2v-1Zm-5,2v1h-3v-1h3Zm-5,2h5v1h-5v-1Zm2,11h-2v-1h2v1Zm-8,7h2v1h-2v-1Zm0-2h13v1H709v-1Zm6,2v1h-2v-1h2Zm3,0v1h-2v-1h2Zm3,0v1h-2v-1h2Zm-10,2h12v1H711v-1Zm11-2h15v1H722v-1Zm4,2h16v1H726v-1Zm15-4h12v1H741v-1Zm7,4h4v1h-4v-1Zm2-2h7v1h-7v-1Zm10-1h-3v-1h3v1Zm-6-2v-1h5v1h-5Zm-1,0h-4v-1h4v1Zm-3-3h10v1H750v-1Zm12-3h-2v-1h2v1Zm-9-1h2v1h-2v-1Zm3,0h2v1h-2v-1Zm-7,3v-1h8v1h-8Zm-31-1h1v1h-1v-1Zm8,1h-2v-1h2v1Zm-9,3h7v1h-7v-1Zm6,2h2v1h-2v-1Zm4-5v-1h8v1h-8Zm-2,1h10v1H725v-1Zm3,2h3v1h-3v-1Zm0,2h7v1h-7v-1Zm5-2h4v1h-4v-1Zm4-2h6v1h-6v-1Zm0,4h3v1h-3v-1Zm3-2h4v1h-4v-1Zm0-6h4v1h-4v-1Zm0,3h-4v-1h12v1h-8Zm5,1h3v1h-3v-1Zm1-4h3v1h-3v-1Zm-1,6h3v1h-3v-1Zm-24-3v-1h2v1h-2Zm-2-3h13v1H719v-1Zm8-8v1h-6v-1h6Zm8,0v1h-7v-1h7Zm5,1h-4v-1h4v1Zm22,6H719v-1h43v1Zm4,6h-5v-1h5v1Zm-8-3h6v1h-6v-1Zm-15,11v-1h4v1h-4Zm-2-3h7v1h-7v-1Zm-32,3h-2v-1h2v1Zm-2-8H694v-1h13v1Zm1-2h-2v-1h2v1Zm4-1v1h-2v-1h2Zm11,3H709v-1h14v1Zm-8-14h-6v-1h6v1Zm-10-3h18v1H705v-1Zm-2,1H688v-1h15v1Zm-23,0v-1h5v1h-5Zm41-4H676v-1h45v1Zm-10-2h-1v-1h1v1Zm2-4h-2v-1h2v1Zm-15-12h-4v-1h4v1Zm-8-2v-1h12v1H690Zm7-6H685v-1h12v1Zm-7-4h-4v-1h4v1Zm-2,2h-7v-1h7v1Zm-10,1h3v1h-3v-1Zm6,2v1h-5v-1h5Zm1,0h4v1h-4v-1Zm-5,6h2v1h-2v-1Zm5,1h-2v-1h2v1Zm-4-3h8v1h-8v-1Zm7-1H678v-1h10v1Zm-12,4v-1h2v1h-2Zm-4-5h5v1h-5v-1Zm8,3h-6v-1h6v1Zm15-11v1h-4v-1h4Zm2,3h-7v-1h7v1Zm51,5v1h-2v-1h2Zm16,10H736v-1h28v1Zm5,45h-9v-1h9v1Z" transform="translate(-669 -431)"></path>
					</svg>
				</div>
			</div>
		</div>
		<section id='header' ref='header'>
			<div class='wrap'>
				<div class='ui-inner-border' v-for='n in ["t","b"]' :class='n' :key='"UIInnerBorder" + n'>
					
				</div>
				<div class='ui-tics' v-for='n in ["t","b"]' :class='n' :key='"UITics" + n'>
					<i class='tic' v-for='n in 50' :key='n * Math.random() + "tic"'></i>
				</div>
				<div class='ui-grid'>
					<div class='ui-box'>
						<h1 class='title' slot='content'><span>The Intergalactic <em>Post</span></em></h1>
						<div class="sub-form">
						<form method="post" action="/subscribe">
							<p>Subscribe to the best intergalactic newsletter</p>
							<input type="text" id="email" name="email" placeholder="somebody@somewhere.com">
							<br>
							<button>
								Subscribe Me To The Truth!
							</button>
						</form>
						<p class="alert"></p>
						</div>
						<div class='ui-fx'>
							<div class='ui-inner-border l'></div>
							<div class='ui-inner-border r'></div>
							<span class='ui-corner' v-for='n in 4' :key='n * Math.random()'></span>
							<div class='ui-batts' :class='batt' v-for='batt in ["l", "r", "t", "b"]' :key='batt + Math.random()'>
								<span class='batt' v-for='n in 2' :key='n * Math.random()'></span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</section>
	</div>
	
	<!-- <script type="text/javascript" src="/static/js/jquery-3.6.0.slim.min.js"></script> -->
	<script src="/static/js/vue.min.js"></script>
	<script src="/static/js/TweenMax.min.js"></script>
	<script src="/static/js/TimelineMax.min.js"></script>
	<script src="/static/js/EasePack.min.js"></script>
	<!-- <script src="/static/js/SplitText.min.js"></script> -->
	<script src="/static/js/EaselPlugin.min.js"></script>
	<script src="/static/js/TextPlugin.min.js"></script>
	<script src="/static/js/three.min.js"></script>
    <script src="/static/js/main.js"></script>
	</body>
</html>
