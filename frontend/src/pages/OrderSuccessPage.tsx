import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { CheckCircle, Package, Truck, MessageCircle } from 'lucide-react';
import { motion } from 'framer-motion';

export const OrderSuccessPage: React.FC = () => {
  const { orderNumber } = useParams<{ orderNumber: string }>();

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12">
      <div className="max-w-lg w-full mx-4">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="bg-white rounded-2xl shadow-sm p-8 text-center"
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200, delay: 0.2 }}
            className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6"
          >
            <CheckCircle size={40} className="text-green-600" />
          </motion.div>

          <h1 className="text-3xl font-bold mb-2">Order Confirmed!</h1>
          <p className="text-gray-500 mb-6">
            Thank you for your purchase. You will receive an SMS confirmation shortly.
          </p>

          <div className="bg-gray-50 rounded-xl p-6 mb-8">
            <p className="text-sm text-gray-500 mb-1">Order Number</p>
            <p className="text-2xl font-mono font-bold text-gray-900">{orderNumber}</p>
          </div>

          <div className="space-y-4 mb-8">
            <div className="flex items-center gap-4 p-4 bg-blue-50 rounded-xl">
              <Package className="text-blue-600" size={24} />
              <div className="text-left">
                <p className="font-medium">Order Processing</p>
                <p className="text-sm text-gray-500">We are preparing your items</p>
              </div>
            </div>
            <div className="flex items-center gap-4 p-4 bg-blue-50 rounded-xl">
              <Truck className="text-blue-600" size={24} />
              <div className="text-left">
                <p className="font-medium">Estimated Delivery</p>
                <p className="text-sm text-gray-500">7-14 business days</p>
              </div>
            </div>
            <div className="flex items-center gap-4 p-4 bg-blue-50 rounded-xl">
              <MessageCircle className="text-blue-600" size={24} />
              <div className="text-left">
                <p className="font-medium">SMS Updates</p>
                <p className="text-sm text-gray-500">You will receive tracking updates via SMS</p>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <Link
              to={`/track/${orderNumber}`}
              className="block w-full bg-gray-900 text-white py-4 rounded-xl font-semibold hover:bg-gray-800 transition-colors"
            >
              Track Order
            </Link>
            <Link
              to="/"
              className="block w-full py-4 rounded-xl border-2 border-gray-200 font-semibold hover:bg-gray-50 transition-colors"
            >
              Continue Shopping
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
};
