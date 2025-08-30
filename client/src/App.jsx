import React from 'react';

function App() {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white rounded-lg shadow-xl p-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800">
            Welcome to React with Tailwind CSS
          </h1>
          <p className="text-gray-500 mt-2">
            A simple starting point for your next project.
          </p>
        </header>
        <main>
          <div className="mb-6">
            <label htmlFor="name" className="block text-gray-700 text-sm font-bold mb-2">
              Name
            </label>
            <input
              type="text"
              id="name"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="Jane Doe"
            />
          </div>
          <div className="flex items-center justify-center">
            <button
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline transition-colors duration-300"
              type="button"
            >
              Submit
            </button>
          </div>
        </main>
        <footer className="text-center mt-8 text-gray-400 text-sm">
          <p>&copy; {new Date().getFullYear()} Your Company. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
}

export default App;