import React from 'react';
import { Link } from 'react-router-dom';
import { ShoppingCart, Eye, Heart } from 'lucide-react';
import { motion } from 'framer-motion';
import { useCartStore } from '../store';
import toast from 'react-hot-toast';

interface Product {
  id: number;
  title: string;
  title_ar?: string;
  images: string[];
  price: {
    final_price: { egp: number; usd: number };
    product_price: { egp: number };
    platform_margin: { percentage: number };
  };
  stock: { quantity: number; status: string };
  category: string;
}

export const ProductCard: React.FC<{ product: Product }> = ({ product }) => {
  const addItem = useCartStore((state) => state.addItem);

  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (product.stock.status !== 'available') {
      toast.error('Product is currently unavailable');
      return;
    }

    addItem({
      id: Date.now(),
      product_id: product.id,
      title: product.title,
      price: product.price.final_price.egp,
      quantity: 1,
      image: product.images[0] || '/placeholder.jpg',
    });

    toast.success('Added to cart!');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5 }}
      className="group relative bg-white rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100"
    >
      {/* Image Container */}
      <Link to={`/product/${product.id}`} className="block relative aspect-[4/5] overflow-hidden bg-gray-50">
        <img
          src={product.images[0] || '/placeholder.jpg'}
          alt={product.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />

        {/* Overlay Actions */}
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300">
          <div className="absolute bottom-4 left-4 right-4 flex gap-2 opacity-0 group-hover:opacity-100 translate-y-4 group-hover:translate-y-0 transition-all duration-300">
            <button
              onClick={handleAddToCart}
              className="flex-1 bg-white text-gray-900 py-3 rounded-xl font-medium flex items-center justify-center gap-2 hover:bg-gray-900 hover:text-white transition-colors shadow-lg"
            >
              <ShoppingCart size={18} />
              Add to Cart
            </button>
          </div>
        </div>

        {/* Stock Badge */}
        {product.stock.status !== 'available' && (
          <div className="absolute top-3 left-3 bg-red-500 text-white px-3 py-1 rounded-full text-xs font-medium">
            Out of Stock
          </div>
        )}

        {/* Category Badge */}
        <div className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm text-gray-700 px-3 py-1 rounded-full text-xs font-medium">
          {product.category}
        </div>
      </Link>

      {/* Content */}
      <div className="p-4">
        <Link to={`/product/${product.id}`}>
          <h3 className="font-semibold text-gray-900 line-clamp-2 mb-1 hover:text-blue-600 transition-colors">
            {product.title}
          </h3>
          {product.title_ar && (
            <p className="text-sm text-gray-500 line-clamp-1 mb-2" dir="rtl">
              {product.title_ar}
            </p>
          )}
        </Link>

        {/* Price Display */}
        <div className="flex items-baseline gap-2 mt-2">
          <span className="text-xl font-bold text-gray-900">
            {product.price.final_price.egp.toLocaleString()} EGP
          </span>
          <span className="text-sm text-gray-400">
            (${product.price.final_price.usd})
          </span>
        </div>

        {/* Price Breakdown Tooltip */}
        <div className="mt-2 text-xs text-gray-500 space-y-1">
          <div className="flex justify-between">
            <span>Product</span>
            <span>{product.price.product_price.egp.toLocaleString()} EGP</span>
          </div>
          <div className="flex justify-between text-green-600">
            <span>Platform Fee ({product.price.platform_margin.percentage}%)</span>
            <span>Included</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export const ProductGrid: React.FC<{ products: Product[] }> = ({ products }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
};
