import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ShoppingCart, Truck, Shield, Clock, ChevronLeft, Star, Share2, Heart } from 'lucide-react';
import { productAPI } from '../services/api';
import { useCartStore } from '../store';
import toast from 'react-hot-toast';

export const ProductDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const addItem = useCartStore((state) => state.addItem);
  const [product, setProduct] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState(0);
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await productAPI.getProduct(Number(id));
        setProduct(response.data);
      } catch (error) {
        toast.error('Product not found');
        navigate('/');
      } finally {
        setIsLoading(false);
      }
    };
    fetchProduct();
  }, [id]);

  const handleAddToCart = () => {
    if (product.stock.status !== 'available') {
      toast.error('Product is currently unavailable');
      return;
    }
    addItem({
      id: Date.now(),
      product_id: product.id,
      title: product.title,
      price: product.price.final_price.egp,
      quantity,
      image: product.images[0] || '/placeholder.jpg',
    });
    toast.success('Added to cart!');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!product) return null;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6 transition-colors"
        >
          <ChevronLeft size={20} />
          Back to products
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          <div className="space-y-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="aspect-square bg-white rounded-2xl overflow-hidden"
            >
              <img
                src={product.images[selectedImage] || '/placeholder.jpg'}
                alt={product.title}
                className="w-full h-full object-cover"
              />
            </motion.div>
            {product.images.length > 1 && (
              <div className="flex gap-2 overflow-x-auto">
                {product.images.map((img: string, i: number) => (
                  <button
                    key={i}
                    onClick={() => setSelectedImage(i)}
                    className={`w-20 h-20 rounded-xl overflow-hidden flex-shrink-0 border-2 transition-all ${
                      selectedImage === i ? 'border-blue-600' : 'border-transparent'
                    }`}
                  >
                    <img src={img} alt="" className="w-full h-full object-cover" />
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="space-y-6">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-medium">
                  {product.category}
                </span>
                <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-medium">
                  {product.supplier.name}
                </span>
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{product.title}</h1>
              {product.title_ar && (
                <p className="text-lg text-gray-600" dir="rtl">{product.title_ar}</p>
              )}
            </div>

            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} size={18} className="text-yellow-400 fill-yellow-400" />
                ))}
              </div>
              <span className="text-sm text-gray-500">(4.8) 128 reviews</span>
            </div>

            <div className="bg-white rounded-2xl p-6 border border-gray-100">
              <div className="flex items-baseline gap-3 mb-4">
                <span className="text-4xl font-bold text-gray-900">
                  {product.price.final_price.egp.toLocaleString()} EGP
                </span>
                <span className="text-lg text-gray-400">
                  (${product.price.final_price.usd})
                </span>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between text-gray-600">
                  <span>Product Price</span>
                  <span>{product.price.product_price.egp.toLocaleString()} EGP</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>International Shipping</span>
                  <span>{product.price.international_shipping.egp.toLocaleString()} EGP</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Customs & Duties ({product.price.custom_duties.percentage}%)</span>
                  <span>{product.price.custom_duties.egp.toLocaleString()} EGP</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Platform Fee ({product.price.platform_margin.percentage}%)</span>
                  <span>{product.price.platform_margin.egp.toLocaleString()} EGP</span>
                </div>
                <div className="border-t pt-2 flex justify-between font-bold text-gray-900">
                  <span>Total</span>
                  <span>{product.price.final_price.egp.toLocaleString()} EGP</span>
                </div>
              </div>
            </div>

            <div className={`flex items-center gap-2 p-4 rounded-xl ${
              product.stock.status === 'available' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
            }`}>
              <div className={`w-3 h-3 rounded-full ${
                product.stock.status === 'available' ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <span className="font-medium">
                {product.stock.status === 'available' 
                  ? `In Stock (${product.stock.quantity} available)` 
                  : 'Out of Stock'}
              </span>
            </div>

            <div className="flex gap-4">
              <div className="flex items-center border border-gray-200 rounded-xl">
                <button onClick={() => setQuantity(Math.max(1, quantity - 1))} className="px-4 py-3 hover:bg-gray-50 transition-colors">-</button>
                <span className="px-4 font-medium">{quantity}</span>
                <button onClick={() => setQuantity(quantity + 1)} className="px-4 py-3 hover:bg-gray-50 transition-colors">+</button>
              </div>
              <button
                onClick={handleAddToCart}
                disabled={product.stock.status !== 'available'}
                className="flex-1 bg-gray-900 text-white py-3 rounded-xl font-semibold hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <ShoppingCart size={20} />
                Add to Cart
              </button>
              <button className="p-3 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors">
                <Heart size={20} />
              </button>
              <button className="p-3 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors">
                <Share2 size={20} />
              </button>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-xl">
                <Truck className="mx-auto text-blue-600 mb-2" size={24} />
                <p className="text-xs font-medium">7-14 Days Delivery</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-xl">
                <Shield className="mx-auto text-green-600 mb-2" size={24} />
                <p className="text-xs font-medium">Secure Payment</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-xl">
                <Clock className="mx-auto text-purple-600 mb-2" size={24} />
                <p className="text-xs font-medium">Real-time Stock</p>
              </div>
            </div>

            <div>
              <h3 className="font-bold text-lg mb-3">Description</h3>
              <p className="text-gray-600 leading-relaxed">{product.description || 'No description available.'}</p>
            </div>

            {product.variants && product.variants.length > 0 && (
              <div>
                <h3 className="font-bold text-lg mb-3">Available Options</h3>
                <div className="flex flex-wrap gap-2">
                  {product.variants.map((variant: any, i: number) => (
                    <button
                      key={i}
                      className="px-4 py-2 border border-gray-200 rounded-lg hover:border-blue-500 hover:text-blue-600 transition-colors"
                    >
                      {variant.sku_id || `Option ${i + 1}`}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
