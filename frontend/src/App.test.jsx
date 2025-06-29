// frontend/src/App.test.jsx
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders upload button', () => {
  render(<App />);
  const uploadButton = screen.getByText(/Upload Image/i);
  expect(uploadButton).toBeInTheDocument();
});
