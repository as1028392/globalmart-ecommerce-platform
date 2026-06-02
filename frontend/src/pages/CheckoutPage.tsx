import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CreditCard, Smartphone, Shield, Truck, CheckCircle, Lock, ShoppingBag } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useCartStore } from '../store';
import { orderAPI } from '../services/api';
import toast from 'react-hot-toast';

type PaymentMethod = 'vodafone_cash' | 'meeza' | 'visa';

export const CheckoutPage: React.FC = () => {
  const navigate = useNavigate();
  const { items, totalPrice, clearCart } = useCartStore();
  const [step, setStep] = useState<'shipping' | 'payment' | 'review'>('shipping');
  const [isProcessing, setIsProcessing] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>('vodafone_cash');
  const [shippingData, setShippingData] = useState({
    fullName: '',
    phone: '',
    address: '',
    city: '',
    governorate: '',
    building: '',
    floor: '',
    apartment: '',
    postalCode: ''
  });

  const handleShippingSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!shippingData.phone.match(/^01[0-2,5]{1}[0-9]{8}$/)) {
      toast.error('Please enter a valid Egyptian phone number');
      return;
    }
    setStep('payment');
  };

  const handlePaymentSubmit = async () => {
    setIsProcessing(true);
    try {
      const response = await orderAPI.createOrder({
        payment_method: paymentMethod,
        shipping_address: shippingData
      });
      clearCart();
      toast.success('Order placed successfully!');
      navigate(`/order-success/${response.data.order.order_number}`);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Payment failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  if (items.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <ShoppingBag size={64} className="mx-auto text-gray-300 mb-4" />
          <h2 className="text-2xl font-bold mb-2">Your cart is empty</h2>
          <button onClick={() => navigate('/')} className="text-blue-600 hover:underline">Continue Shopping</button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-center mb-12">
          {['Shipping', 'Payment', 'Review'].map((s, i) => (
            <React.Fragment key={s}>
              <div className={`flex items-center gap-2 ${i <= ['shipping', 'payment', 'review'].indexOf(step) ? 'text-blue-600' : 'text-gray-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${i <= ['shipping', 'payment', 'review'].indexOf(step) ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
                  {i + 1}
                </div>
                <span className="font-medium">{s}</span>
              </div>
              {i < 2 && <div className="w-16 h-0.5 bg-gray-300 mx-4" />}
            </React.Fragment>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <AnimatePresence mode="wait">
              {step === 'shipping' && (
                <motion.div key="shipping" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} className="bg-white rounded-2xl shadow-sm p-8">
                  <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                    <Truck className="text-blue-600" /> Shipping Details
                  </h2>
                  <form onSubmit={handleShippingSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
                        <input required type="text" value={shippingData.fullName} onChange={(e) => setShippingData({ ...shippingData, fullName: e.target.value })} className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all" placeholder="As shown on ID" />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number *</label>
                        <input required type="tel" value={shippingData.phone} onChange={(e) => setShippingData({ ...shippingData, phone: e.target.value })} className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all" placeholder="01XXXXXXXXX" />
                        <p className="text-xs text-gray-500 mt-1">For SMS notifications and delivery contact</p>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Street Address *</label>
                      <input required type="text" value={shippingData.address} onChange={(e) => setShippingData({ ...shippingData, address: e.target.value })} className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all" placeholder="Street name, area, landmark" />
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Governorate *</label>
                        <select required value={shippingData.governorate} onChange={(e) => setShippingData({ ...shippingData, governorate: e.target.value })} className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all">
                          <option value="">Select Governorate</option>
                          <option value="Cairo">Cairo</option>
                          <option value="Giza">Giza</option>
                          <option value="Alexandria">Alexandria</option>
                          <option value="Sharqia">Sharqia</option>
                          <option value="Dakahlia">Dakahlia</option>
                          <option value="Beheira">Beheira</option>
                          <option value="Gharbia">Gharbia</option>
                          <option value="Kafr El Sheikh">Kafr El Sheikh</option>
                          <option value="Monufia">Monufia</option>
                          <option value="Qalyubia">Qalyubia</option>
                          <option value="Damietta">Damietta</option>
                          <option value="Port Said">Port Said</option>
                          <option value="Ismailia">Ismailia</option>
                          <option value="Suez">Suez</option>
                          <option value="North Sinai">North Sinai</option>
                          <option value="South Sinai">South Sinai</option>
                          <option value="Faiyum">Faiyum</option>
                          <option value="Beni Suef">Beni Suef</option>
                          <option value="Minya">Minya</option>
                          <option value="Asyut">Asyut</option>
                          <option value="Sohag">Sohag</option>
                          <option value="Qena">Qena</option>
                          <option value="Luxor">Luxor</option>
                          <option value="Aswan">Aswan</option>
                          <option value="Red Sea">Red Sea</option>
                          <option value="New Valley">New Valley</option>
                          <option value="Matrouh">Matrouh</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">City *</label>
                        <input required type="text" value={shippingData.city} onChange={(e) => setShippingData({ ...shippingData, city: e.target.value })} className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all" />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Postal Code</label>
                        <input type="text" value={shippingData.postalCode} onChange={(e) => setShippingData({ ...shippingData, postalCode: e.target.value })} className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all" />
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Building</label>
                        <input type="text" value={shippingData.building} onChange={(e) => setShippingData({ ...shippingData, building: e.target.value })} className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all" />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Floor</label>
                        <input type="text" value={shippingData.floor} onChange={(e) => setShippingData({ ...shippingData, floor: e.target.value })} className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all" />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Apartment</label>
                        <input type="text" value={shippingData.apartment} onChange={(e) => setShippingData({ ...shippingData, apartment: e.target.value })} className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all" />
                      </div>
                    </div>
                    <button type="submit" className="w-full bg-gray-900 text-white py-4 rounded-xl font-semibold hover:bg-gray-800 transition-colors mt-6">
                      Continue to Payment
                    </button>
                  </form>
                </motion.div>
              )}

              {step === 'payment' && (
                <motion.div key="payment" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} className="bg-white rounded-2xl shadow-sm p-8">
                  <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                    <Lock className="text-blue-600" /> Payment Method
                  </h2>
                  <div className="space-y-4">
                    <button onClick={() => setPaymentMethod('vodafone_cash')} className={`w-full p-6 rounded-xl border-2 transition-all flex items-center gap-4 ${paymentMethod === 'vodafone_cash' ? 'border-red-500 bg-red-50' : 'border-gray-200 hover:border-gray-300'}`}>
                      <div className="w-12 h-12 bg-red-600 rounded-xl flex items-center justify-center text-white">
                        <Smartphone size={24} />
                      </div>
                      <div className="text-left flex-1">
                        <h3 className="font-semibold text-lg">Vodafone Cash</h3>
                        <p className="text-gray-500 text-sm">Pay using your Vodafone Cash wallet</p>
                      </div>
                      {paymentMethod === 'vodafone_cash' && <CheckCircle className="text-red-600" size={24} />}
                    </button>

                    <button onClick={() => setPaymentMethod('meeza')} className={`w-full p-6 rounded-xl border-2 transition-all flex items-center gap-4 ${paymentMethod === 'meeza' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}`}>
                      <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center text-white">
                        <CreditCard size={24} />
                      </div>
                      <div className="text-left flex-1">
                        <h3 className="font-semibold text-lg">Meeza Card</h3>
                        <p className="text-gray-500 text-sm">Pay with your Meeza debit card</p>
                      </div>
                      {paymentMethod === 'meeza' && <CheckCircle className="text-blue-600" size={24} />}
                    </button>

                    <button onClick={() => setPaymentMethod('visa')} className={`w-full p-6 rounded-xl border-2 transition-all flex items-center gap-4 ${paymentMethod === 'visa' ? 'border-green-500 bg-green-50' : 'border-gray-200 hover:border-gray-300'}`}>
                      <div className="w-12 h-12 bg-green-600 rounded-xl flex items-center justify-center text-white">
                        <CreditCard size={24} />
                      </div>
                      <div className="text-left flex-1">
                        <h3 className="font-semibold text-lg">Visa / Mastercard</h3>
                        <p className="text-gray-500 text-sm">Pay with international credit card</p>
                      </div>
                      {paymentMethod === 'visa' && <CheckCircle className="text-green-600" size={24} />}
                    </button>
                  </div>
                  <div className="flex gap-4 mt-8">
                    <button onClick={() => setStep('shipping')} className="flex-1 py-4 rounded-xl border-2 border-gray-200 font-semibold hover:bg-gray-50 transition-colors">Back</button>
                    <button onClick={() => setStep('review')} className="flex-1 bg-gray-900 text-white py-4 rounded-xl font-semibold hover:bg-gray-800 transition-colors">Review Order</button>
                  </div>
                </motion.div>
              )}

              {step === 'review' && (
                <motion.div key="review" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} className="bg-white rounded-2xl shadow-sm p-8">
                  <h2 className="text-2xl font-bold mb-6">Order Review</h2>
                  <div className="space-y-6">
                    <div className="bg-gray-50 p-4 rounded-xl">
                      <h3 className="font-semibold mb-2">Shipping Address</h3>
                      <p className="text-gray-600">{shippingData.fullName}</p>
                      <p className="text-gray-600">{shippingData.phone}</p>
                      <p className="text-gray-600">{shippingData.address}</p>
                      <p className="text-gray-600">{shippingData.city}, {shippingData.governorate}</p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-xl">
                      <h3 className="font-semibold mb-2">Payment Method</h3>
                      <p className="text-gray-600 capitalize">{paymentMethod.replace('_', ' ')}</p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-xl">
                      <h3 className="font-semibold mb-2">Items ({items.length})</h3>
                      {items.map((item) => (
                        <div key={item.id} className="flex justify-between py-2 border-b border-gray-200 last:border-0">
                          <span>{item.title} x{item.quantity}</span>
                          <span className="font-medium">{(item.price * item.quantity).toLocaleString()} EGP</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="flex gap-4 mt-8">
                    <button onClick={() => setStep('payment')} className="flex-1 py-4 rounded-xl border-2 border-gray-200 font-semibold hover:bg-gray-50 transition-colors">Back</button>
                    <button onClick={handlePaymentSubmit} disabled={isProcessing} className="flex-1 bg-gray-900 text-white py-4 rounded-xl font-semibold hover:bg-gray-800 transition-colors disabled:opacity-50 flex items-center justify-center gap-2">
                      {isProcessing ? (
                        <><div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />Processing...</>
                      ) : (
                        <><Lock size={18} />Pay {totalPrice().toLocaleString()} EGP</>
                      )}
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-sm p-6 sticky top-6">
              <h3 className="text-xl font-bold mb-6">Order Summary</h3>
              <div className="space-y-4 mb-6">
                {items.map((item) => (
                  <div key={item.id} className="flex gap-3">
                    <img src={item.image} alt={item.title} className="w-16 h-16 object-cover rounded-lg" />
                    <div className="flex-1">
                      <p className="text-sm font-medium line-clamp-2">{item.title}</p>
                      <p className="text-sm text-gray-500">Qty: {item.quantity}</p>
                    </div>
                    <p className="font-medium">{(item.price * item.quantity).toLocaleString()}</p>
                  </div>
                ))}
              </div>
              <div className="space-y-3 border-t pt-4">
                <div className="flex justify-between text-gray-600">
                  <span>Subtotal</span>
                  <span>{totalPrice().toLocaleString()} EGP</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Shipping</span>
                  <span className="text-green-600">Included</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Customs & Duties</span>
                  <span className="text-green-600">Included</span>
                </div>
                <div className="flex justify-between text-xl font-bold border-t pt-3">
                  <span>Total</span>
                  <span>{totalPrice().toLocaleString()} EGP</span>
                </div>
              </div>
              <div className="mt-6 space-y-3">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Shield size={16} className="text-green-600" />
                  <span>Secure SSL Encryption</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Truck size={16} className="text-blue-600" />
                  <span>7-14 Business Days Delivery</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
