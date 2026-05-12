// Configuração da URL da API
const API = "http://127.0.0.1:8001";

// ==========================================
// HELPERS (Requisições Genéricas)
// ==========================================
async function get(url) {
    try {
        const res = await fetch(API + url);
        if (!res.ok) return null;
        return await res.json();
    } catch (e) {
        console.error("Erro ao buscar dados:", e);
        return null;
    }
}

// ==========================================
// AUTENTICAÇÃO
// ==========================================
async function login() {
    const email = document.getElementById("email").value;
    const senha = document.getElementById("senha").value;

    const res = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, senha })
    });
    
    if (res.ok) {
        const data = await res.json();
        localStorage.setItem("usuario", JSON.stringify(data.usuario));
        window.location.href = `/home`; 
    } else {
        alert("E-mail ou senha incorretos!");
    }
}

// ==========================================
// GESTÃO DE IMÓVEIS
// ==========================================

function verDetalhes(id) {
    // Redireciona para a página de detalhes com o ID na URL
    window.location.href = `/static/detalhes_imovel.html?id=${id}`;
}

async function cadastrarImovel() {
    try {
        // 1. Upload de Fotos
        const fileInput = document.getElementById("foto");
        let fotosUrls = [];

        if (fileInput && fileInput.files.length > 0) {
            for (let file of fileInput.files) {
                const formData = new FormData();
                formData.append("file", file);
                const resUpload = await fetch(API + "/upload", { method: "POST", body: formData });
                const dataUpload = await resUpload.json();
                fotosUrls.push(dataUpload.url);
            }
        }

        // 2. Geocodificação (Transformar endereço em Lat/Log)
        const rua = document.getElementById("rua").value;
        const numero = document.getElementById("numero").value;
        const bairro = document.getElementById("bairro").value;
        const enderecoCompleto = `${rua}, ${numero}, ${bairro}, Uberlandia, MG, Brazil`;

        let lat = 0;
        let lon = 0;

        try {
            const geoRes = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(enderecoCompleto)}`);
            const geoData = await geoRes.json();
            if (geoData && geoData.length > 0) {
                lat = parseFloat(geoData[0].lat);
                lon = parseFloat(geoData[0].lon);
            }
        } catch (err) { console.warn("Não foi possível obter coordenadas."); }

        // 3. Montagem dos Dados
        const dados = {
            titulo: document.getElementById("titulo").value,
            tipo: document.getElementById("tipo").value,
            bairro: bairro,
            regiao: document.getElementById("regiao").value,
            quartos: Number(document.getElementById("quartos").value),
            banheiros: Number(document.getElementById("banheiros").value),
            vagas: Number(document.getElementById("vagas").value),
            valor: Number(document.getElementById("valor").value),
            endereco_rua: rua,
            endereco_numero: numero,
            latitude: lat,
            longitude: lon,
            descricao: document.getElementById("observacoes").value, 
            fotos: fotosUrls.join(",")
        };

        const res = await fetch(API + "/imoveis", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dados)
        });

        if (res.ok) {
            alert("✅ Imóvel cadastrado com sucesso!");
            window.location.href = "/home";
        }
    } catch (e) {
        alert("Erro ao salvar imóvel.");
    }
}

async function buscarImoveis() {
    const tipo = document.getElementById("tipoBusca")?.value;
    const bairro = document.getElementById("bairroBusca")?.value;
    const vMax = document.getElementById("valorMax")?.value;

    const params = new URLSearchParams();
    if (tipo) params.append("tipo", tipo);
    if (bairro) params.append("bairro", bairro);
    if (vMax) params.append("valor_max", vMax);
    
    // Removido o parâmetro "t" que causava erro 422
    const lista = await get(`/imoveis/busca?${params.toString()}`);
    renderizarImoveis(lista || []);
}

function renderizarImoveis(lista) {
    const container = document.getElementById("listaImoveis");
    if (!container) return;

    if (lista.length === 0) {
        container.innerHTML = "<p style='text-align:center; padding:20px;'>Nenhum imóvel encontrado.</p>";
        return;
    }

    container.innerHTML = lista.map(i => {
        const primeiraFoto = i.fotos ? i.fotos.split(',')[0] : '';
        const imgUrl = primeiraFoto.startsWith('http') ? primeiraFoto : API + primeiraFoto;
        
        return `
        <div class="card" style="cursor: pointer; border: 1px solid #eee; border-radius: 8px; overflow: hidden; margin-bottom: 20px; transition: 0.3s;" onclick="verDetalhes(${i.id})">
            <img src="${primeiraFoto ? imgUrl : 'https://via.placeholder.com/300x200?text=Sem+Foto'}" 
                 style="width:100%; height:180px; object-fit:cover;">
            <div style="padding: 15px;">
                <h3 style="margin:0; color:#4b3f2f;">${i.titulo}</h3>
                <p style="color:#666; font-size:0.9rem; margin: 5px 0;">📍 ${i.bairro}</p>
                <p style="font-size:1.1rem; color:#a1866f;"><strong>R$ ${Number(i.valor).toLocaleString('pt-BR')}</strong></p>
                <button onclick="event.stopPropagation(); deletarImovel(${i.id})" 
                        style="background:#fdeaea; color:#c0392b; border:1px solid #c0392b; width:100%; padding:8px; border-radius:4px; cursor:pointer; margin-top:10px;">
                    🗑️ Excluir
                </button>
            </div>
        </div>
    `}).join("");
}

async function deletarImovel(id) {
    if (confirm("Deseja realmente excluir este imóvel?")) {
        const res = await fetch(API + `/imoveis/${id}`, { method: "DELETE" });
        if (res.ok) buscarImoveis();
    }
}

// ==========================================
// GESTÃO DE CLIENTES
// ==========================================

function verDetalhesCliente(id) {
    window.location.href = `/static/detalhes_cliente.html?id=${id}`;
}

async function cadastrarCliente() {
    const nome = document.getElementById("nome")?.value;
    const telefone = document.getElementById("telefone")?.value;
    const email = document.getElementById("email")?.value;

    if (!nome || !telefone) return alert("Nome e Telefone são obrigatórios!");

    const res = await fetch(API + "/clientes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome, telefone, email })
    });

    if (res.ok) {
        alert("✅ Cliente cadastrado!");
        window.location.href = "/static/lista_clientes.html";
    }
}

async function carregarClientes() {
    const clientes = await get("/clientes");
    const container = document.getElementById("listaClientes");
    if (!container || !clientes) return;

    container.innerHTML = clientes.map(c => `
        <div class="card" style="display:flex; justify-content:space-between; align-items:center; padding:15px; margin-bottom:10px; border:1px solid #eee; border-radius: 8px;">
            <div onclick="verDetalhesCliente(${c.id})" style="cursor:pointer; flex-grow: 1;">
                <strong style="font-size: 1.1rem; color: #4b3f2f;">${c.nome}</strong><br>
                <span style="color: #666;">📞 ${c.telefone}</span>
            </div>
            <button onclick="deletarCliente(${c.id})" style="background:#fdeaea; color:#c0392b; border:1px solid #c0392b; padding:8px 12px; border-radius:4px; cursor:pointer; margin-left:10px;">
                Excluir
            </button>
        </div>
    `).join("");
}

async function deletarCliente(id) {
    if (confirm("Excluir cliente?")) {
        const res = await fetch(API + `/clientes/${id}`, { method: "DELETE" });
        if (res.ok) carregarClientes();
    }
}

// ==========================================
// FUNÇÕES DE EDIÇÃO DE CLIENTE
// ==========================================

async function salvarEdicaoCliente(id, dados) {
    try {
        const res = await fetch(`${API}/clientes/${id}`, {
            method: "PUT", // Método para atualização
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dados)
        });

        if (res.ok) {
            alert("✅ Dados do cliente atualizados com sucesso!");
            // Redireciona de volta para a página de detalhes ou lista
            window.location.href = `/static/detalhes_cliente.html?id=${id}`;
        } else {
            const erro = await res.json();
            alert("❌ Erro ao atualizar: " + (erro.detail || "Erro desconhecido"));
        }
    } catch (e) {
        console.error("Erro na requisição:", e);
        alert("Erro ao conectar com o servidor.");
    }
}

// ==========================================
// DINAMISMO (Bairros/Regiões)
// ==========================================
async function popularFiltros() {
    const bairros = await get("/bairros");
    const regioes = await get("/regioes");

    const preencher = (id, lista) => {
        const el = document.getElementById(id);
        if (!el || !lista) return;
        el.innerHTML = `<option value="">Selecione...</option>` + 
                        lista.map(item => `<option value="${item}">${item}</option>`).join("");
    };

    preencher("bairro", bairros);
    preencher("bairroBusca", bairros);
    preencher("regiao", regioes);
    preencher("regiaoBusca", regioes);
}

// ==========================================
// INICIALIZAÇÃO
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
    popularFiltros();
    // Identifica qual página estamos para carregar a função correta
    if (document.getElementById("listaImoveis")) buscarImoveis();
    if (document.getElementById("listaClientes")) carregarClientes();
});