import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Truck, Package, CheckCircle, MapPin, Clock, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { orderAPI } from '../services/api';

interface TrackingEvent {
  status: string;
  location: string;
  timestamp: string;
  description: string;
}

export const OrderTrackingPage: React.FC = () => {
  const { trackingNumber } = useParams<{ trackingNumber: string }>();
  const [trackingData, setTrackingData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchTracking = async () => {
      try {
        const response = await orderAPI.trackOrder(trackingNumber!);
        setTrackingData(response.data);
      } catch (error) {
        console.error('Tracking error:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchTracking();
  }, [trackingNumber]);

  const statusSteps = [
    { key: 'pending', label: 'Order Placed', icon: Package },
    { key: 'paid', label: 'Payment Confirmed', icon: CheckCircle },
    { key: 'shipped', label: 'Shipped', icon: Truck },
    { key: 'in_customs', label: 'In Customs', icon: AlertCircle },
    { key: 'out_for_delivery', label: 'Out for Delivery', icon: MapPin },
    { key: 'delivered', label: 'Delivered', icon: CheckCircle },
  ];

  const currentStepIndex = statusSteps.findIndex(s => s.key === trackingData?.current_status);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-3xl mx-auto px-4">
        <div className="bg-white rounded-2xl shadow-sm p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-2">Track Your Order</h1>
            <p className="text-gray-500">Tracking Number: <span className="font-mono font-medium">{trackingNumber}</span></p>
          </div>

          {/* Progress Timeline */}
          <div className="relative mb-12">
            <div className="absolute top-5 left-0 right-0 h-1 bg-gray-200 rounded-full">
              <motion.div
                className="h-full bg-blue-600 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${((currentStepIndex + 1) / statusSteps.length) * 100}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
              />
            </div>
            <div className="relative flex justify-between">
              {statusSteps.map((step, index) => {
                const Icon = step.icon;
                const isActive = index <= currentStepIndex;
                const isCurrent = index === currentStepIndex;

                return (
                  <div key={step.key} className="flex flex-col items-center">
                    <motion.div
                      initial={false}
                      animate={{
                        backgroundColor: isActive ? '#2563eb' : '#e5e7eb',
                        scale: isCurrent ? 1.2 : 1
                      }}
                      className="w-10 h-10 rounded-full flex items-center justify-center text-white z-10"
                    >
                      <Icon size={20} />
                    </motion.div>
                    <span className={`text-xs mt-2 font-medium ${isActive ? 'text-blue-600' : 'text-gray-400'}`}>
                      {step.label}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Current Status */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-8">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white">
                <Truck size={24} />
              </div>
              <div>
                <h3 className="font-bold text-lg">{trackingData?.detailed_status}</h3>
                <p className="text-gray-600">{trackingData?.location}</p>
                <p className="text-sm text-gray-500 mt-1">
                  Last updated: {new Date(trackingData?.last_update).toLocaleString('en-EG')}
                </p>
              </div>
            </div>
          </div>

          {/* Tracking History */}
          <div className="space-y-4">
            <h3 className="font-bold text-lg mb-4">Tracking History</h3>
            {trackingData?.tracking_history?.map((event: TrackingEvent, index: number) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex gap-4 p-4 bg-gray-50 rounded-xl"
              >
                <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                  <Clock size={16} className="text-gray-600" />
                </div>
                <div>
                  <p className="font-medium">{event.status}</p>
                  <p className="text-sm text-gray-500">{event.description}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(event.timestamp).toLocaleString('en-EG')}
                  </p>
                </div>
              </motion.div>
            )) || (
              <p className="text-gray-500 text-center py-8">No tracking history available yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
