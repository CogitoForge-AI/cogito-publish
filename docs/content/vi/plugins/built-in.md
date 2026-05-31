---
title: Plugin có sẵn
order: 1
---

# Plugin có sẵn

## Tier 1 - Markdown sang HTML

| Plugin | Hook | Phụ thuộc | Mục đích |
|--------|------|-----------|----------|
| `ReadFile` | `discover`, `load` | stdlib | Tìm file nguồn và đọc nội dung thô của chúng. |
| `Frontmatter` | `parse` | pyyaml | Tách khối `---` và phân tích nó dưới dạng YAML. |
| `Markdown` | `transform` | `markdown` | Render body thành HTML. |
| `Template` | `render` | `jinja2` | Bọc nội dung trong một layout Jinja2, phát ra một Output. |
| `WriteFile` | `emit` | stdlib | Ghi các output vào thư mục `out`. |
| `StaticFiles` | `emit` | stdlib | Sao chép một thư mục asset (CSS/JS/ảnh) vào output. |

### ReadFile

```python
ReadFile(patterns=("*.md", "*.markdown"))
```

Đi qua `src`, thu thập các file khớp dưới dạng đối tượng `Source`, rồi đọc văn
bản thô của từng file.

### Frontmatter

Phân tích khối `---` ở đầu dưới dạng YAML bằng PyYAML (`yaml.safe_load`), nên hỗ
trợ trọn vẹn đặc tả YAML. Lỗi phân tích mang theo một mốc `file:line:column`
chính xác mà CLI in ra gọn gàng và `pyssg serve` render thành một lớp phủ
(overlay). Cần extra `pyssg[frontmatter]`.

### Markdown

```python
Markdown(extensions=["fenced_code", "tables"])
```

Render `body` thành `content` bằng python-markdown. Các extension được truyền
thẳng qua.

### Template

```python
Template(directory="layouts", default_layout="default.html", partials_dir="partials")
```

Render mỗi trang bằng Jinja2 và phát ra một `Output`. Template được chọn bởi một
[lookup cascade](/vi/templating/lookup-cascade/) (frontmatter `layout` thắng
trước, rồi `type`/`section`/`_default` theo `kind`). Hỗ trợ
[kế thừa](/vi/templating/inheritance/) native và một hàm
[`partial()`](/vi/templating/partials/). Template nhận `content`, `page`,
`partial`, và mọi khóa của `build.meta` (`site`, `collections`, `menus`). Xem mục
[Templating](/vi/templating/) để có câu chuyện đầy đủ.

### WriteFile

```python
WriteFile(clean=True)
```

Ghi mọi `Output`. Với `clean=True` thư mục output được dọn rỗng trước.

### StaticFiles

```python
StaticFiles(directory="assets", dest="assets")
```

Sao chép mọi file dưới `directory` vào `out/dest`, giữ nguyên cây con. Nó chạy
sau `WriteFile`, nên sống sót qua một bản build có clean. Dùng nó cho CSS, JS,
ảnh và bất cứ thứ gì được phục vụ nguyên trạng.

### Fingerprint

```python
Fingerprint(directory="assets", dest="assets", extensions=(".css", ".js"))
```

Băm nội dung asset để chống cache cũ (cache-busting): `style.css` trở thành
`style.<hash>.css`, và tham chiếu được viết lại ở mọi nơi để trình duyệt có thể
cache mỗi file mãi mãi mà vẫn lấy file mới ngay khi nội dung của nó thay đổi.

Nó sở hữu thư mục asset từ đầu tới cuối, nên hãy dùng nó **thay cho**
`StaticFiles` đối với thư mục đó: file khớp `extensions` được phát ra dưới tên đã
băm; mọi thứ khác được sao chép nguyên trạng. Tham chiếu được phân giải theo hai
cách:

- tự động, bằng cách viết lại URL logic (`/assets/style.css`) thành URL đã băm
  trong mọi output HTML -- bao gồm cả thẻ `og:image`/canonical từ plugin Seo,
  nên không thứ gì khác cần biết hash;
- tường minh, qua một biến toàn cục template `asset()`:
  `{{ asset('/assets/style.css') }}` trả về URL đã băm (các đường dẫn không xác
  định đi qua nguyên trạng).

Chỉ tham chiếu bên trong HTML được viết lại; `url(...)` bên trong CSS được để yên.
Tập mặc định `.css`/`.js` tránh trường hợp một ảnh đã fingerprint được tham chiếu
từ CSS và lẽ ra sẽ hỏng. Plugin này là tùy chọn (opt-in): thêm `Fingerprint()`
vào danh sách plugin trong `pyssg.config.py` của bạn.

## Tier 2 - cấu trúc linh hoạt

| Plugin | Hook (stage) | Mục đích |
|--------|--------------|----------|
| `Permalink` | `collect` (-200) | Quyết định URL và đường dẫn output của mỗi trang. |
| `Collections` | `collect` (-100) | Gom nhóm trang theo tag, thư mục hoặc một predicate. |
| `Listing` | `collect` (0) | Biến một collection thành một hoặc nhiều trang danh sách. |
| `Navigation` | `collect` (100) | Dựng các menu có tên và liên kết prev/next. |

### Permalink

```python
Permalink()                              # pretty URLs: foo.md -> /foo/
Permalink(pattern="/blog/:year/:slug/")  # pattern-based
Permalink(pretty=False)                  # foo.md -> /foo.html
```

Ghi đè theo từng trang qua frontmatter: `permalink: /custom/path/`. Các
placeholder gồm `:slug`, `:year`, `:month`, `:day`, `:title` và bất kỳ khóa
frontmatter nào.

### Collections

```python
Collections(by_tag=True, by_folder=True)
Collections(custom={"featured": lambda s: s.frontmatter.get("featured")})
```

Dựng `build.meta["collections"]`: một dict các nhóm có tên, có thứ tự. Mặc định
sắp xếp `auto` (theo ngày khi có, nếu không thì theo `order` rồi tới title).

### Listing

```python
Listing(collection="blog", base_url="/blog/", title="Blog", page_size=10)
Listing(kind="tag", base_url="/tags/:name/", title=":name")
```

Biến một collection thành (các) trang danh sách. Phân trang chỉ là tùy chọn
`page_size`. Template nhận `page.entries` (các tham chiếu trang) và, khi có phân
trang, `page.paginator`.

### Navigation

```python
Navigation(mode="folder", sequential=True)   # docs sidebar + prev/next
Navigation(mode="frontmatter")               # pages declaring `menu: main`
Navigation(items=[...])                       # explicit tree from config
```

Ghi `build.meta["menus"][name]` dưới dạng một cây các nút nav. Với
`sequential=True` nó còn liên kết các trang kề nhau qua `page.prev` / `page.next`.

## Tier 3 - output và tối ưu

Các plugin này tạo ra file phụ hoặc hậu xử lý output đã build. Tất cả đều chỉ
dùng thư viện chuẩn.

| Plugin | Hook | Mục đích |
|--------|------|----------|
| `Sitemap` | `generate` | Phát ra một `sitemap.xml` cho mọi trang công khai. |
| `Rss` | `generate` | Phát ra một feed RSS 2.0 từ một collection. |
| `Robots` | `generate` | Phát ra một `robots.txt` có chỉ thị `Sitemap:`. |
| `Redirects` | `generate` | Giữ các URL cũ còn sống sau khi một trang dời đi. |
| `Minify` | `optimize` | Thu nhỏ output HTML, bảo toàn `pre`/`code`/`script`. |

### Sitemap

```python
Sitemap(path="sitemap.xml")
```

Thêm một mục `<url>` cho mỗi trang công khai (trang có URL, không phải draft).
Vị trí tuyệt đối dùng `site["base_url"]`; nếu không có, các URL tương-đối-từ-gốc
được phát ra. Frontmatter `date` trở thành `<lastmod>`.

### Rss

```python
Rss(collection="blog", path="feed.xml", title="My Blog", limit=20)
```

Biến `limit` trang mới nhất của một collection thành một feed RSS 2.0. Metadata
của channel mặc định lấy từ tùy chọn `site` (`title`, `tagline`, `base_url`);
`pubDate` của item lấy từ frontmatter `date`, và `description` từ `description`
hoặc `summary`. Không làm gì nếu collection không tồn tại.

### Robots

```python
Robots(disallow=["/private/"], sitemap=True)
```

Phát ra một `robots.txt`. Mặc định nó cho phép mọi crawler và, khi
`site["base_url"]` được đặt, nối thêm một chỉ thị `Sitemap:` tuyệt đối. Đặt
`site["private"] = True` lật cả file thành "cấm tất cả" -- một công tắc bảo vệ
duy nhất cho các bản triển khai staging. Dùng `groups=[{user_agent, allow,
disallow}]` cho các quy tắc theo từng user-agent.

### Redirects

```python
Redirects(
    rules={"/old-path/": "/new-path/"},   # explicit, for non-page targets
    emit_redirects_file=False,            # also emit a Netlify/CF _redirects
)
```

Giữ các URL cũ còn hoạt động sau khi một trang dời đi. Redirect đến từ hai nguồn,
frontmatter thắng khi hòa:

1. frontmatter `aliases` của một trang (các URL cũ của nó):

   ```yaml
   ---
   title: New home
   aliases: [/old-home/, /2020/intro/]
   ---
   ```

2. `rules` tường minh cho các đích không phải là một trang đã build (một URL bên
   ngoài, một trang đã xóa).

Mặc định nó ghi một trang HTML meta-refresh nhỏ xíu cho mỗi URL cũ -- mang đi
được tới mọi host tĩnh, bao gồm GitHub Pages. Mỗi trang mang một
`<meta http-equiv="refresh">`, một liên kết canonical (tuyệt đối khi
`site["base_url"]` được đặt) và một script dự phòng. Đặt
`emit_redirects_file=True` để còn phát ra một manifest `_redirects` cho các phản
hồi 3xx phía server thực sự trên Netlify và Cloudflare Pages (mặc định
`status=301`). Một redirect có đường dẫn đụng độ với một trang thật đã build sẽ
bị bỏ kèm cảnh báo, nên trang luôn thắng.

Plugin này là tùy chọn (opt-in): thêm `Redirects()` vào danh sách plugin trong
`pyssg.config.py` của bạn.

### Minify

```python
Minify(suffixes=(".html", ".htm"))
```

Gộp khoảng trắng dư thừa và loại bỏ comment trong các output khớp. Nó thận trọng:
nội dung của `pre`, `code`, `textarea`, `script` và `style` được để nguyên, và
comment điều kiện của IE được giữ lại.

### MarkdownPage

```python
MarkdownPage(
    llms_txt=True,             # also emit an /llms.txt index
    html_link=True,            # inject a <link rel="alternate"> hint
    include_title=False,       # prepend "# <title>" if the body has no heading
    include_frontmatter=False, # prepend the original frontmatter block
)
```

Phục vụ một bản sao Markdown thô của mỗi trang để các AI agent có thể đọc nguồn
thay vì phân tích HTML đã render. Ba lớp bổ trợ cho nhau, mỗi lớp có thể bật/tắt:

1. Một file `.md` đồng hành cho từng trang, theo quy ước "nối `.md` vào URL":
   `/guide/intro/` cũng được phục vụ tại `/guide/intro.md`, và trang chủ `/` tại
   `/index.md`.
2. Một chỉ mục `llms.txt` tại gốc trang ([llmstxt.org](https://llmstxt.org)): một
   file markdown liệt kê mọi trang và liên kết tới bản sao `.md` của nó. Liên kết
   là tuyệt đối khi `site["base_url"]` được đặt.
3. Một gợi ý `<link rel="alternate" type="text/markdown">` được tiêm vào `<head>`
   của mỗi trang, để một agent rơi vào trang HTML có thể tìm thấy bản sao.

Nội dung của bản đồng hành mặc định chỉ là `source.body`; bật `include_title`
và/hoặc `include_frontmatter` để làm phong phú nó. Các trang listing nhân tạo và
draft bị bỏ qua (chúng không có markdown do tác giả viết).

## Bật tier 3 qua preset

Mỗi preset chấp nhận `sitemap=True` / `minify=True` / `markdown_pages=True`, và
`blog()` sinh ra một feed RSS mặc định (`rss=True`). Xem
[Preset](/vi/plugins/presets/).

## Công cụ

### Statistics

```python
Statistics(top_n=5, by_type=True, json_path=None)
```

In ra một bản tóm tắt build sau khi mọi artifact được ghi: số lượng source (kèm
số trang dẫn xuất/sinh ra), tổng số file và kích thước, phân tách theo loại file,
và các file lớn nhất. Các con số là dạng lai - số liệu logic đến từ build trong
bộ nhớ, trong khi kích thước và loại file được đọc từ đĩa dưới `out`, nên các
asset tĩnh được `StaticFiles` sao chép cũng được tính.

```text
Build summary
  Sources:  17
  Files:    19    Total: 89.5 KB    Build: 124 ms
  By type:
    .html    17     84.6 KB
    .css      1      3.5 KB
    .xml      1      1.4 KB
  Largest:
    plugins/built-in/index.html   10.5 KB
    ...
```

Nó là tùy chọn (opt-in): thêm `Statistics()` vào `config.plugins`. Khi bật, nó
thay thế thông điệp build một dòng mặc định. Nó giữ im lặng dưới `pyssg serve` để
tránh làm nhiễu vòng lặp rebuild.

Truyền `json_path` để còn ghi báo cáo dưới dạng JSON (hữu ích trong CI để theo
dõi kích thước build theo thời gian):

```python
Statistics(json_path="public/_stats.json")
```
