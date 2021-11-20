const puppeteer = require('puppeteer')
const fs = require('fs')

const URL = process.env['URL_FILESHARING'] 
const URL_LOGIN = URL + '/login'
const EMAIL = process.env['EMAIL_FILESHARING']
const PASSWORD = process.env['PASSWORD_FILESHARING']

const TIMEOUT = 1000*5 // 5s

async function visit(url) {

    console.log('Running browser to visit "%s"', url);

	const browser = await puppeteer.launch({ 
        headless: true,
        args: [
            '--disable-default-apps',
            '--disable-extensions',
            '--disable-gpu',
            '--disable-sync',
            '--disable-translate',
            '--hide-scrollbars',
            '--metrics-recording-only',
            '--mute-audio',
            '--no-first-run',
            '--no-sandbox',
            '--safebrowsing-disable-auto-update'
        ],
        executablePath: '/usr/bin/google-chrome'})

	let page = await browser.newPage()
    await page.setDefaultNavigationTimeout(TIMEOUT);
	
	try{
        //authenticate
		await page.goto(URL_LOGIN)
        await page.waitForSelector('#inputEmail')
        await page.focus('#inputEmail')
        await page.keyboard.type(EMAIL, {delay: 10})
        await page.focus('#inputPassword')
        await page.keyboard.type(PASSWORD, {delay: 10})
        await page.click('#submit')

        await page.waitForNavigation({waitUntil: 'networkidle2'});

        //console.log(await page.cookies())
		
        // Contacting URL after auth
        //console.log(url)
		await page.goto(url)

        // wait in the page
		await new Promise(resolve => setTimeout(resolve, TIMEOUT));
		await page.close()
		await browser.close()
	} catch (e){
		await browser.close()
		console.log(e)
        //throw(e)
  	}

}

module.exports = { visit }
