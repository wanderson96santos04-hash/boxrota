import { useEffect, useState } from "react"

export function useMobile() {
  const [mobile, setMobile] = useState(window.innerWidth < 768)

  useEffect(() => {
    const handleResize = () => {
      setMobile(window.innerWidth < 768)
    }

    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  return mobile
}