// أنيميشن التحويل بين اللوحات
const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');

registerBtn.addEventListener('click', () => {
    container.classList.add("active");
});

loginBtn.addEventListener('click', () => {
    container.classList.remove("active");
});

// رابط السيرفر المحلي (تأكد أن السيرفر يعمل على منفذ 5000)
const BACKEND_URL = 'http://localhost:5000';

// ربط معالجة إنشاء الحساب (Register)
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('regName').value;
    const phone = document.getElementById('regPhone').value;
    const password = document.getElementById('regPassword').value;

    try {
        const response = await fetch(`${BACKEND_URL}/api/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, phone, password })
        });

        const data = await response.json();
        if (response.ok) {
            alert(`نجاح: ${data.message}`);
            container.classList.remove("active"); // نقله لصفحة تسجيل الدخول بعد النجاح
        } else {
            alert(`خطأ: ${data.message}`);
        }
    } catch (error) {
        alert('فشل الاتصال بسيرفر الـ Backend');
    }
});

// ربط معالجة تسجيل الدخول (Login)
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const phone = document.getElementById('loginPhone').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch(`${BACKEND_URL}/api/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, password })
        });

        const data = await response.json();
        if (response.ok) {
            alert(`أهلاً بك: ${data.message}`);
            // هنا يمكنك توجيه المستخدم لصفحة المتجر الرئيسية لاحقاً
        } else {
            alert(`خطأ: ${data.message}`);
        }
    } catch (error) {
        alert('فشل الاتصال بسيرفر الـ Backend');
    }
});
 