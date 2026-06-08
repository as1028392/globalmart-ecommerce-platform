const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');

registerBtn.addEventListener('click', () => {
    container.classList.add("active");
});

loginBtn.addEventListener('click', () => {
    container.classList.remove("active");
});

let currentLang = 'ar'; 

const dictionary = {
    ar: {
        htmlDir: "rtl",
        langBtnText: "English",
        createAccount: "إنشاء حساب جديد",
        usePhoneSignup: "أو استخدم رقم جوالك للتسجيل",
        namePlaceholder: "الاسم الكامل",
        phoneSignupPlaceholder: "رقم الجوال (مثال: 010XXXXXXXX)",
        passPlaceholder: "كلمة المرور",
        btnSignup: "إنشاء الحساب",
        signinTitle: "تسجيل الدخول",
        usePhoneSignin: "أو ادخل باستخدام رقم الجوال وكلمة المرور",
        phoneSigninPlaceholder: "رقم الجوال",
        forgetPass: "هل نسيت كلمة المرور؟",
        btnSignin: "تسجيل الدخول",
        welcomeBack: "مرحباً بك مجدداً!",
        welcomeDesc: "لتظل على اتصال معنا، يرجى تسجيل الدخول ببياناتك الشخصية",
        helloFriend: "أهلاً بك يا صديقنا!",
        helloDesc: "أدخل بياناتك الشخصية وابدأ رحلة التسوق العالمي معنا الآن",
        otpAlert: "تم إرسال كود التحقق (OTP) إلى جوالك بنجاح!",
        loginAlert: "تم تسجيل الدخول بنجاح!"
    },
    en: {
        htmlDir: "ltr",
        langBtnText: "العربية",
        createAccount: "Create Account",
        usePhoneSignup: "or use your mobile number for registration",
        namePlaceholder: "Full Name",
        phoneSignupPlaceholder: "Mobile Number (e.g., 010XXXXXXXX)",
        passPlaceholder: "Password",
        btnSignup: "Sign Up",
        signinTitle: "Sign In",
        usePhoneSignin: "or use your mobile number and password",
        phoneSigninPlaceholder: "Mobile Number",
        forgetPass: "Forgot Your Password?",
        btnSignin: "Sign In",
        welcomeBack: "Welcome Back!",
        welcomeDesc: "To keep connected with us please login with your personal info",
        helloFriend: "Hello, Friend!",
        helloDesc: "Enter your personal details and start your global shopping journey",
        otpAlert: "OTP verification code sent to your mobile successfully!",
        loginAlert: "Logged in successfully!"
    }
};

function toggleLanguage() {
    currentLang = currentLang === 'ar' ? 'en' : 'ar';
    const langData = dictionary[currentLang];
    const htmlTag = document.getElementById('app-html');
    if(htmlTag) {
        htmlTag.setAttribute('dir', langData.htmlDir);
        htmlTag.setAttribute('lang', currentLang);
    }
    
    document.getElementById('lang-btn').innerText = langData.langBtnText;
    document.getElementById('login').innerText = langData.btnSignin;
    document.getElementById('register').innerText = langData.btnSignup;
    
    document.getElementById('txt-create-account').innerText = langData.createAccount;
    document.getElementById('txt-use-phone-signup').innerText = langData.usePhoneSignup;
    document.getElementById('input-name').setAttribute('placeholder', langData.namePlaceholder);
    document.getElementById('input-phone-signup').setAttribute('placeholder', langData.phoneSignupPlaceholder);
    document.getElementById('input-pass-signup').setAttribute('placeholder', langData.passPlaceholder);
    document.getElementById('btn-signup-submit').innerText = langData.btnSignup;
    
    document.getElementById('txt-signin-title').innerText = langData.signinTitle;
    document.getElementById('txt-use-phone-signin').innerText = langData.usePhoneSignin;
    document.getElementById('input-phone-signin').setAttribute('placeholder', langData.phoneSigninPlaceholder);
    document.getElementById('input-pass-signin').setAttribute('placeholder', langData.passPlaceholder);
    document.getElementById('txt-forget-pass').innerText = langData.forgetPass;
    document.getElementById('btn-signin-submit').innerText = langData.btnSignin;
    
    document.getElementById('txt-welcome-back').innerText = langData.welcomeBack;
    document.getElementById('txt-welcome-desc').innerText = langData.welcomeDesc;
    document.getElementById('txt-hello-friend').innerText = langData.helloFriend;
    document.getElementById('txt-hello-desc').innerText = langData.helloDesc;
}

// ==========================================
// الربط الفعلي بالسيرفر باستخدام Fetch
// ==========================================

// 1. ربط زر إنشاء الحساب (Sign Up)
document.getElementById('btn-signup-submit').addEventListener('click', async function(e) {
    e.preventDefault();
    
    const name = document.getElementById('input-name').value;
    const phone = document.getElementById('input-phone-signup').value;
    const password = document.getElementById('input-pass-signup').value;

    if(!name || !phone || !password) {
        alert(currentLang === 'ar' ? "برجاء ملء جميع الحقول!" : "Please fill all fields!");
        return;
    }

    try {
        // الـ Fetch هنا يأخذ البيانات ويرسلها للسيرفر المحلي منفذ 5000
        const response = await fetch('http://localhost:5000/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, phone, password })
        });

        const data = await response.json();

        if (response.ok) {
            alert(currentLang === 'ar' ? "تم إرسال كود التحقق (OTP) إلى جوالك بنجاح!" : "OTP verification code sent!");
        } else {
            alert(data.message || "Error");
        }
    } catch (error) {
        console.error("Error:", error);
        alert(currentLang === 'ar' ? "فشل الاتصال بالسيرفر! تأكد أن سيرفر الـ backend يعمل" : "Server connection failed!");
    }
});

document.getElementById('btn-signin-submit').addEventListener('click', function(e) {
    e.preventDefault();
    alert(dictionary[currentLang].loginAlert);
