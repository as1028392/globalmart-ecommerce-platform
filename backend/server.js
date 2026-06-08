const express = require('express');
const cors = require('cors');
const app = express();

app.use(express.json());
app.use(cors()); // لتسمح للـ Frontend بالاتصال بالـ Backend بدون حظر أمني

// استقبال بيانات إنشاء الحساب من الواجهة
app.post('/api/register', (req, res) => {
    const { name, phone, password } = req.body;
    
    console.log(`تم استقبال طلب تسجيل لـ: ${name} برقم: ${phone}`);

    // [منطقة مخصصة لربط Twilio لاحقاً]
    // هنا نأمر Twilio بإرسال الـ OTP هاتفياً
    
    // نرد على الواجهة بأن كل شيء تمام ليظهر التنبيه للعميل
    return res.status(200).json({ success: true, message: "OTP Sent" });
});

// استقبال بيانات تسجيل الدخول من الواجهة
app.post('/api/login', (req, res) => {
    const { phone, password } = req.body;

    // هنا يتم التحقق من قاعدة البيانات هل الحساب موجود وكلمة المرور صحيحة أم لا
    if (phone === "01000000000" && password === "123456") {
        return res.status(200).json({ success: true, message: "Logged In" });
    } else {
        return res.status(400).json({ success: false, message: "بيانات الدخول غير صحيحة" });
    }
});

// تشغيل السيرفر على منفذ 5000
app.listen(5000, () => {
    console.log('Server is running on port 5000');
});
