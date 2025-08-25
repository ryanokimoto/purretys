import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50">
      <div className="container mx-auto px-4 py-16">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-purple-800 mb-4">
            🐱 Purretys
          </h1>
          <p className="text-xl text-gray-600">
            Collaborative Virtual Pet Care
          </p>
        </header>
        
        <main className="max-w-2xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="text-center">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                Welcome to Purretys!
              </h2>
              <p className="text-gray-600 mb-6">
                Get ready to take care of your virtual cat with friends!
              </p>
              
              <div className="space-y-4">
                <button 
                  onClick={() => setCount(count + 1)}
                  className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors duration-200 font-medium"
                >
                  Pet the Cat ({count} pets)
                </button>
              </div>
              
              <div className="mt-8 p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">
                  🚧 Development Mode - Ready to build your pet care app!
                </p>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App