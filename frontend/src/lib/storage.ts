export const storage = {
  setAccessToken(token: string) {
    localStorage.setItem("access_token", token)
  },

  getAccessToken() {
    return localStorage.getItem("access_token")
  },

  setRefreshToken(token: string) {
    localStorage.setItem("refresh_token", token)
  },

  getRefreshToken() {
    return localStorage.getItem("refresh_token")
  },

  clear() {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
  }
}