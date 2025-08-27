import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import App from './App'

test('renders logos and heading', () => {
  render(<App />)

  expect(screen.getByAltText(/Vite logo/i)).toBeInTheDocument()
  expect(screen.getByAltText(/React logo/i)).toBeInTheDocument()

  expect(screen.getByText(/Vite \+ React/i)).toBeInTheDocument()
})

test('increments counter on button click', () => {
  render(<App />)

  const button = screen.getByRole('button', { name: /count is 0/i })
  expect(button).toBeInTheDocument()

  fireEvent.click(button)
  expect(screen.getByRole('button', { name: /count is 1/i })).toBeInTheDocument()

  fireEvent.click(button)
  expect(screen.getByRole('button', { name: /count is 2/i })).toBeInTheDocument()
})
