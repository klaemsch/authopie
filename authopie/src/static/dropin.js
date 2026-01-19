/**
 * CONSTANTS
 */
// find location of this script
const SCRIPT_URL = new URL(document.currentScript.src)
const BASE_URL = SCRIPT_URL.origin

// make sure context is secure
if (SCRIPT_URL.protocol == 'http:' && !(SCRIPT_URL.hostname == 'localhost')) {
    throw new Error('WebAuthn only works in secure contexts! (localhost or HTTPS)')
}

const SIGNIN_ELEMNT_ID = 'mpasSignin'
const POPUP_BASE_URL = BASE_URL + '/connect/authorize'
const STYLE_URL = BASE_URL + '/static/dropin.css'

/**
 * ADD CUSTOM CSS
 */
const link = document.createElement('link')
link.rel = 'stylesheet'
link.type = 'text/css'
link.href = STYLE_URL
document.head.appendChild(link)

/**
 * GET SIGNIN ELEMENT AND ATTRIBUTES
 */

// get sign in element (preferable a div) to modify
const signInElement = document.getElementById(SIGNIN_ELEMNT_ID)
if (!signInElement) throw new Error('No signin element found. Please declare with id mpasSignin')

const client_id = signInElement.getAttribute('client_id')
if (!client_id) throw new Error('client_id attribute not found')

const redirect_uri = signInElement.getAttribute('redirect_uri')
if (!redirect_uri) throw new Error('redirect_uri attribute not found')

const scope = signInElement.getAttribute('scope') || 'openid'
const response_type = signInElement.getAttribute('response_type') || 'id_token code'

/**
 * ADD TO HTML
 */

// add content of signin container
const left = document.createElement('p')
left.innerText = 'M'

const right = document.createElement('p')
right.innerText = 'Sign in with MPAS'

// insert html inside sign in container
signInElement.appendChild(left)
signInElement.appendChild(right)

// add styles
signInElement.classList.add('signin-container')
left.classList.add('icon-col')
right.classList.add('text-col')

/**
 * POP UP
 */

// https://openid.net/specs/openid-connect-core-1_0.html#ImplicitAuthRequest
let authRequestURL = new URLSearchParams()

authRequestURL.append('client_id', client_id)
authRequestURL.append('redirect_uri', redirect_uri)
authRequestURL.append('scope', scope)
authRequestURL.append('response_type', response_type)
// authRequestURL.append('response_mode', '')
authRequestURL.append('state', crypto.randomUUID())
authRequestURL.append('nonce', crypto.randomUUID())

// opens sign in popup
const openPopUp = () => {
    window.open(POPUP_BASE_URL + '?' + authRequestURL.toString(), 'popup', 'width=600,height=800')
}

// add click event -> opens pop up
signInElement.addEventListener('click', openPopUp)