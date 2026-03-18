import { useState, useCallback } from "react";
import { T } from "../theme";

interface SkuItem {
  itemId: string;
  name: string;
  size: string;
  available: boolean;
  quantity: number;
  price: number;
  image: string;
}

interface ProductResult {
  productName: string;
  brand: string;
  link: string;
  items: SkuItem[];
}

const NIKE_CATALOG = "https://www.nike.cl/api/catalog_system/pub/products/search";

async function searchSku(query: string): Promise<ProductResult | null> {
  const isSkuId = /^\d+$/.test(query.trim());
  const url = isSkuId
    ? `${NIKE_CATALOG}?fq=skuId:${query.trim()}`
    : `${NIKE_CATALOG}?ft=${encodeURIComponent(query.trim())}&_from=0&_to=0`;

  const resp = await fetch(url, {
    headers: {
      Accept: "application/json",
      "User-Agent": "Mozilla/5.0",
    },
  });
  if (!resp.ok) return null;
  const data = await resp.json();
  if (!data || data.length === 0) return null;

  const product = data[0];
  const items: SkuItem[] = (product.items || []).map((item: any) => {
    const seller = item.sellers?.[0]?.commertialOffer || {};
    return {
      itemId: item.itemId,
      name: item.name || product.productName,
      size: item.Talla?.[0] || item.Talle?.[0] || item.Size?.[0] || "—",
      available: seller.IsAvailable ?? false,
      quantity: seller.AvailableQuantity ?? 0,
      price: seller.Price ?? 0,
      image: item.images?.[0]?.imageUrl || "",
    };
  });

  return {
    productName: product.productName,
    brand: product.brand || "Nike",
    link: product.link || "",
    items,
  };
}

export function SKUs({ t }: { t: T }) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ProductResult | null>(null);
  const [error, setError] = useState("");
  const [savedSkus, setSavedSkus] = useState<string[]>(() => {
    try { return JSON.parse(sessionStorage.getItem("aoda_skus") || "[]"); } catch { return []; }
  });

  const handleSearch = useCallback(async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await searchSku(query);
      if (res) {
        setResult(res);
      } else {
        setError("Producto no encontrado");
      }
    } catch {
      setError("Error de conexión con Nike.cl");
    } finally {
      setLoading(false);
    }
  }, [query]);

  const addSku = (sku: string) => {
    if (!savedSkus.includes(sku)) {
      const next = [...savedSkus, sku];
      setSavedSkus(next);
      try { sessionStorage.setItem("aoda_skus", JSON.stringify(next)); } catch {}
    }
  };

  const removeSku = (sku: string) => {
    const next = savedSkus.filter(s => s !== sku);
    setSavedSkus(next);
    try { sessionStorage.setItem("aoda_skus", JSON.stringify(next)); } catch {}
  };

  return (
    <div style={{ padding: 28, display: "flex", flexDirection: "column", height: "100vh" }}>

      {/* header */}
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ color: t.text, fontSize: 20, fontWeight: 700, marginBottom: 6 }}>SKUs</h2>
        <p style={{ color: t.textDim, fontSize: 12, margin: 0 }}>
          Busca productos en Nike.cl por SKU o nombre — datos en tiempo real
        </p>
      </div>

      {/* search bar */}
      <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
        <input
          placeholder="SKU (ej: 134427) o nombre..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === "Enter" && !loading && handleSearch()}
          style={{
            flex: 1, background: t.row, border: `1px solid ${t.border}`,
            borderRadius: 8, padding: "10px 14px", color: t.text,
            fontSize: 13, outline: "none", fontFamily: "Consolas, monospace",
          }}
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          style={{
            background: loading ? t.greenDim : t.green,
            color: loading ? t.green : "#000", border: "none",
            borderRadius: 8, padding: "10px 20px", fontSize: 13,
            fontWeight: 700, cursor: loading ? "wait" : "pointer",
          }}
        >
          {loading ? "..." : "Buscar"}
        </button>
      </div>

      {/* saved skus bar */}
      {savedSkus.length > 0 && (
        <div style={{
          display: "flex", gap: 6, marginBottom: 16, flexWrap: "wrap",
          alignItems: "center",
        }}>
          <span style={{ color: t.textDim, fontSize: 11, fontWeight: 600 }}>GUARDADOS:</span>
          {savedSkus.map(sku => (
            <span key={sku} style={{
              background: t.greenDim, border: `1px solid ${t.green}40`,
              borderRadius: 8, padding: "3px 10px", fontSize: 11,
              color: t.green, fontFamily: "Consolas", display: "flex",
              alignItems: "center", gap: 6,
            }}>
              {sku}
              <span
                onClick={() => removeSku(sku)}
                style={{ cursor: "pointer", opacity: 0.6, fontSize: 13 }}
              >×</span>
            </span>
          ))}
        </div>
      )}

      {/* error */}
      {error && (
        <div style={{
          background: t.redDim, border: `1px solid ${t.red}40`,
          borderRadius: 8, padding: "12px 16px", marginBottom: 16,
          color: t.red, fontSize: 12, fontWeight: 600,
        }}>
          {error}
        </div>
      )}

      {/* results */}
      {result && (
        <div style={{ flex: 1, overflow: "auto" }}>

          {/* product header */}
          <div style={{
            background: t.panel, border: `1px solid ${t.border}`,
            borderRadius: "12px 12px 0 0", padding: "16px 20px",
            display: "flex", alignItems: "center", gap: 16,
          }}>
            {result.items[0]?.image && (
              <img
                src={result.items[0].image}
                alt=""
                style={{ width: 64, height: 64, objectFit: "contain", borderRadius: 8, background: t.row }}
              />
            )}
            <div>
              <div style={{ color: t.text, fontSize: 15, fontWeight: 700 }}>{result.productName}</div>
              <div style={{ color: t.textDim, fontSize: 11, marginTop: 2 }}>{result.brand}</div>
            </div>
            <div style={{ marginLeft: "auto", textAlign: "right" }}>
              <div style={{ color: t.green, fontSize: 14, fontWeight: 700 }}>
                {result.items[0]?.price > 0 ? `$${result.items[0].price.toLocaleString()}` : "—"}
              </div>
              <div style={{ color: t.textDim, fontSize: 11 }}>
                {result.items.filter(i => i.available).length}/{result.items.length} tallas con stock
              </div>
            </div>
          </div>

          {/* size grid header */}
          <div style={{
            display: "grid",
            gridTemplateColumns: "70px 1fr 80px 90px 80px 70px",
            gap: 8, padding: "10px 20px",
            background: t.panel, borderLeft: `1px solid ${t.border}`,
            borderRight: `1px solid ${t.border}`,
          }}>
            {["SKU", "NOMBRE", "TALLA", "STOCK", "PRECIO", ""].map((h, i) => (
              <span key={i} style={{
                color: t.textDim, fontSize: 10, fontWeight: 700,
                letterSpacing: 0.8,
              }}>{h}</span>
            ))}
          </div>

          {/* size rows */}
          <div style={{
            background: t.panel, border: `1px solid ${t.border}`,
            borderRadius: "0 0 12px 12px", overflow: "hidden",
          }}>
            {result.items.map((item, i) => (
              <div key={i} style={{
                display: "grid",
                gridTemplateColumns: "70px 1fr 80px 90px 80px 70px",
                gap: 8, padding: "12px 20px",
                borderBottom: i < result.items.length - 1 ? `1px solid ${t.border}` : "none",
                alignItems: "center",
              }}>
                <span style={{ color: t.textMed, fontSize: 11, fontFamily: "Consolas" }}>
                  {item.itemId}
                </span>
                <span style={{ color: t.text, fontSize: 12 }}>{item.name}</span>
                <span style={{ color: t.text, fontSize: 13, fontWeight: 600 }}>{item.size}</span>
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span style={{
                    width: 7, height: 7, borderRadius: "50%",
                    background: item.available ? t.green : t.red,
                  }} />
                  <span style={{
                    color: item.available ? t.green : t.red,
                    fontSize: 11, fontWeight: 600,
                  }}>
                    {item.available ? `${item.quantity} uds` : "Agotado"}
                  </span>
                </div>
                <span style={{ color: t.green, fontSize: 12, fontWeight: 600 }}>
                  {item.price > 0 ? `$${item.price.toLocaleString()}` : "—"}
                </span>
                <button
                  onClick={() => addSku(item.itemId)}
                  disabled={savedSkus.includes(item.itemId)}
                  style={{
                    background: savedSkus.includes(item.itemId) ? t.row : t.greenDim,
                    border: `1px solid ${savedSkus.includes(item.itemId) ? t.border : t.green}`,
                    color: savedSkus.includes(item.itemId) ? t.textDim : t.green,
                    borderRadius: 6, padding: "4px 10px", fontSize: 11,
                    cursor: savedSkus.includes(item.itemId) ? "default" : "pointer",
                    fontWeight: 600,
                  }}
                >
                  {savedSkus.includes(item.itemId) ? "✓" : "+"}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* empty state */}
      {!result && !error && !loading && (
        <div style={{
          flex: 1, display: "flex", flexDirection: "column",
          alignItems: "center", justifyContent: "center", gap: 10,
        }}>
          <span style={{ fontSize: 32 }}>🔎</span>
          <span style={{ color: t.textDim, fontSize: 13 }}>Busca un SKU o nombre de producto</span>
          <span style={{ color: t.textDim, fontSize: 11 }}>
            Ejemplo: <span style={{ color: t.green, fontFamily: "Consolas", cursor: "pointer" }}
              onClick={() => { setQuery("134427"); }}>134427</span>
          </span>
        </div>
      )}
    </div>
  );
}