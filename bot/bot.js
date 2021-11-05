const puppeteer = require('puppeteer')
const fs = require('fs')

const URL = process.env['URL_FILESHARING'] 
const URL_LOGIN = URL + '/login'
const EMAIL = process.env['EMAIL_FILESHARING']
const PASSWORD = process.env['PASSWORD_FILESHARING']

const TIMEOUT = 1000*3

async function visit(url) {

    console.log('Running browser to visit "%s"', url);

	const browser = await puppeteer.launch({ 
        args: ['--no-sandbox'],
        executablePath: '/usr/bin/chromium'})

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

        //console.log(await page.cookies())
		
        // Contacting URL after auth
        //console.log(url)
		//await page.goto(url)

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