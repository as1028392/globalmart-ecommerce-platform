// أنيميشن التحويل بين اللوحات (Sign In & Sign Up)
const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');

registerBtn.addEventListener('click', () => {
    container.classList.add("active");
});

loginBtn.addEventListener('click', () => {
    container.classList.remove("active");
});

// رابط السيرفر المحلي (تأكد أن السيرفر شغال في الـ Terminal على منفذ 5000)
const BACKEND_URL = 'http://localhost:5000';

// كود تسجيل حساب جديد (Register)
const signUpForm = document.querySelector('.sign-up form');
signUpForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // منع الصفحة من إعادة التحميل التلقائي

    // التقاط القيم من الحقول المجهزة
    const name = signUpForm.querySelector('input[placeholder="Name"]').value;
    const phone = signUpForm.querySelector('input[placeholder="Phone Number"]').value;
    const password = signUpForm.querySelector('input[placeholder="Password"]').value;

    try {
        // إرسال البيانات إلى الـ Backend عبر طلب POST
        const response = await fetch(`${BACKEND_URL}/api/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, phone, password })
        });

        const data = await response.json();

        if (response.ok) {
            alert(`تم إرسال كود التحقق بنجاح! 🎉\nالرسالة من السيرفر: ${data.message}`);
            container.classList.remove("active"); // نقله تلقائياً لصفحة تسجيل الدخول
        } else {
            alert(`خطأ: ${data.message}`);
        }
    } catch (error) {
        console.error('حدث خطأ أثناء الاتصال بالسيرفر:', error);
        alert('فشل الاتصال بسيرفر الـ Backend. تأكد أن السيرفر يعمل!');
    }
});

// كود تسجيل الدخول (Sign In)
const signInForm = document.querySelector('.sign-in form');
signInForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const phone = signInForm.querySelector('input[placeholder="Phone Number"]').value;
    const password = signInForm.querySelector('input[placeholder="Password"]').value;

    try {
        const response = await fetch(`${BACKEND_URL}/api/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ phone, password })
        });

        const data = await response.json();

        if (response.ok) {
            alert(`تم تسجيل الدخول بنجاح! 👋\nمرحباً بك: ${data.message}`);
        } else {
            alert(`خطأ: ${data.message}`);
        }
    } catch (error) {
        console.error('حدث خطأ أثناء الاتصال بالسيرفر:', error);
        alert('فشل الاتصال بسيرفر الـ Backend.');
    }
});