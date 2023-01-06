import './styles.css';

function App({ Component, pageProps }) {
  return (
    <>
      <head>
        <title>Generated Insights</title>
      </head>
      <Component {...pageProps} />
    </>
  )
}
export default App;
