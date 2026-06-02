import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { X, Plus, Minus, ShoppingBag, Truck, Shield, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useCartStore } from '../store';
import toast from 'react-hot-toast';

export const SmartCart: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  const { items, removeItem, updateQuantity, totalItems, totalPrice, clearCart } = useCartStore();
  const [isCheckingOut, setIsCheckingOut] = useState(false);

  const handleCheckout = () => {
    if (items.length === 0) {
      toast.error('Your cart is empty');
      return;
    }
    setIsCheckingOut(true);
    window.location.href = '/checkout';
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
          />
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 h-full w-full max-w-md bg-white shadow-2xl z-50 flex flex-col"
          >
            <div className="flex items-center justify-between p-6 border-b">
              <div className="flex items-center gap-3">
                <ShoppingBag className="text-blue-600" size={24} />
                <h2 className="text-xl font-bold">Shopping Cart</h2>
                <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-sm font-medium">
                  {totalItems()}
                </span>
              </div>
              <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                <X size={20} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {items.length === 0 ? (
                <div className="text-center py-12">
                  <ShoppingBag size={64} className="mx-auto text-gray-300 mb-4" />
                  <p className="text-gray-500 text-lg">Your cart is empty</p>
                  <button onClick={onClose} className="mt-4 text-blue-600 font-medium hover:underline">
                    Continue Shopping
                  </button>
                </div>
              ) : (
                <AnimatePresence mode="popLayout">
                  {items.map((item) => (
                    <motion.div
                      key={item.id}
                      layout
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      className="flex gap-4 bg-gray-50 p-4 rounded-xl"
                    >
                      <img src={item.image} alt={item.title} className="w-20 h-20 object-cover rounded-lg" />
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 line-clamp-2">{item.title}</h4>
                        <p className="text-blue-600 font-semibold mt-1">{item.price.toLocaleString()} EGP</p>
                        <div className="flex items-center gap-3 mt-2">
                          <button onClick={() => updateQuantity(item.id, item.quantity - 1)} className="w-8 h-8 flex items-center justify-center bg-white rounded-lg border hover:bg-gray-100">
                            <Minus size={14} />
                          </button>
                          <span className="font-medium w-8 text-center">{item.quantity}</span>
                          <button onClick={() => updateQuantity(item.id, item.quantity + 1)} className="w-8 h-8 flex items-center justify-center bg-white rounded-lg border hover:bg-gray-100">
                            <Plus size={14} />
                          </button>
                          <button onClick={() => removeItem(item.id)} className="ml-auto text-red-500 hover:text-red-700 p-1">
                            <X size={18} />
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              )}
            </div>

            {items.length > 0 && (
              <div className="border-t p-6 space-y-4 bg-gray-50">
                <div className="flex items-center justify-center gap-6 text-xs text-gray-500">
                  <div className="flex items-center gap-1">
                    <Shield size={14} className="text-green-600" />
                    <span>Secure Payment</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Truck size={14} className="text-blue-600" />
                    <span>Fast Shipping</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-gray-600">
                    <span>Subtotal</span>
                    <span>{totalPrice().toLocaleString()} EGP</span>
                  </div>
                  <div className="flex justify-between text-gray-600">
                    <span>Shipping & Duties</span>
                    <span className="text-green-600">Included</span>
                  </div>
                  <div className="flex justify-between text-xl font-bold border-t pt-2">
                    <span>Total</span>
                    <span>{totalPrice().toLocaleString()} EGP</span>
                  </div>
                </div>
                <button onClick={handleCheckout} disabled={isCheckingOut} className="w-full bg-gray-900 text-white py-4 rounded-xl font-semibold flex items-center justify-center gap-2 hover:bg-gray-800 transition-colors disabled:opacity-50">
                  {isCheckingOut ? 'Processing...' : 'Proceed to Checkout'}
                  <ArrowRight size={18} />
                </button>
                <button onClick={clearCart} className="w-full text-gray-500 text-sm hover:text-red-600 transition-colors">
                  Clear Cart
                </button>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export const CartIcon: React.FC<{ onClick: () => void }> = ({ onClick }) => {
  const totalItems = useCartStore((state) => state.totalItems);
  return (
    <button onClick={onClick} className="relative p-2 hover:bg-gray-100 rounded-full transition-colors">
      <ShoppingBag size={24} />
      {totalItems() > 0 && (
        <motion.span initial={{ scale: 0 }} animate={{ scale: 1 }} className="absolute -top-1 -right-1 bg-blue-600 text-white text-xs w-5 h-5 flex items-center justify-center rounded-full font-bold">
          {totalItems()}
        </motion.span>
      )}
    </button>
  );
};
