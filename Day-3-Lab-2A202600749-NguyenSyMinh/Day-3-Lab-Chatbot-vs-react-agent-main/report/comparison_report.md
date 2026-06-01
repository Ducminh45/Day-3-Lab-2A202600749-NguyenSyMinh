# Comparative Evaluation Report: Chatbot vs ReAct Agent

This report contains a systematic performance comparison between a standard LLM Chatbot baseline and a ReAct Agent (loop). Both are tested against Vietnamese Stock Market Analysis scenarios.

## 📊 Run Configuration
- **Timestamp**: 2026-06-01 16:55:27
- **LLM Provider**: `OPENAI`
- **Model Name**: `gpt-4o-mini`

---

## 📈 Quantitative Performance Summary

| Test Case | System | Latency (ms) | Steps (LLM Calls) | Prompt Tokens | Completion Tokens | Total Tokens | Estimated Cost ($) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **TC_01_SIMPLE** (Simple tool lookup (Single ticker price)) | Chatbot | 3,071 | 1 | 254 | 61 | 315 | $0.00315 |
| | ReAct Agent | 2,042 | 2 | 1,858 | 64 | 1,922 | $0.01922 |
| **TC_02_MEDIUM** (Multi-step lookup (HPG fundamental + technical)) | Chatbot | 16,635 | 1 | 262 | 889 | 1,151 | $0.01151 |
| | ReAct Agent | 16,742 | 4 | 4,303 | 906 | 5,209 | $0.05209 |
| **TC_03_COMPLEX** (Highly complex comparison (TCB vs FPT)) | Chatbot | 16,852 | 1 | 269 | 960 | 1,229 | $0.01229 |
| | ReAct Agent | 15,233 | 5 | 5,821 | 1,114 | 6,935 | $0.06935 |

---

## 🔍 Qualitative Response Analysis

### [TC_01_SIMPLE] Giá cổ phiếu hiện tại của FPT là bao nhiêu?

#### 🤖 Chatbot Baseline (Gọi LLM 1 Lần)
> **Phân tích**: Chatbot trả lời trực tiếp mà không có công cụ. Do đó, các thông tin cụ thể (như giá cổ phiếu chính xác tại thời điểm mock, báo cáo tài chính cụ thể, chỉ số kỹ thuật hiện tại) có thể bị thiếu, lỗi thời, hoặc bị chatbot tự suy đoán (hallucinate).
>
```
Xin lỗi, nhưng tôi không có khả năng truy cập thông tin thời gian thực, bao gồm giá cổ phiếu hiện tại của FPT. Tuy nhiên, tôi có thể giúp bạn phân tích doanh nghiệp này dựa trên các thông tin đã biết. Nếu bạn cần, hãy cho tôi biết!
```

#### 🧠 ReAct Agent (Thought -> Action -> Observation Loop)
> **Phân tích**: Agent liên tục suy luận và gọi các công cụ liên quan như `get_stock_price`, `get_financial_metrics`, `get_technical_indicators` để tích hợp dữ liệu thực tế chính xác vào câu trả lời cuối cùng (`Final Answer`).
>
```
Giá cổ phiếu hiện tại của FPT là 135,200 VND, tăng 1.5% so với hôm qua.
```

### [TC_02_MEDIUM] Hãy phân tích chi tiết mã cổ phiếu HPG về cả mặt cơ bản và phân tích kỹ thuật.

#### 🤖 Chatbot Baseline (Gọi LLM 1 Lần)
> **Phân tích**: Chatbot trả lời trực tiếp mà không có công cụ. Do đó, các thông tin cụ thể (như giá cổ phiếu chính xác tại thời điểm mock, báo cáo tài chính cụ thể, chỉ số kỹ thuật hiện tại) có thể bị thiếu, lỗi thời, hoặc bị chatbot tự suy đoán (hallucinate).
>
```
### 1. Tổng Quan về mã cổ phiếu HPG (Công ty Cổ phần Tập đoàn Hòa Phát)

Công ty Cổ phần Tập đoàn Hòa Phát (HPG) là một trong những doanh nghiệp hàng đầu trong ngành sản xuất thép tại Việt Nam. HPG chuyên sản xuất và tiêu thụ các sản phẩm thép xây dựng, thép cuộn, và các sản phẩm liên quan. Với lợi thế về quy mô sản xuất lớn, công nghệ tiên tiến và mạng lưới phân phối rộng khắp, Hòa Phát đã chiếm lĩnh được một phần lớn thị trường thép trong nước.

### 2. Phân Tích Cơ Bản (Fundamental Analysis)

**Doanh thu và Lợi nhuận:** 
- HPG thường có doanh thu và lợi nhuận ổn định hàng năm, nhờ vào hoạt động sản xuất thép mạnh mẽ và sự tăng trưởng nhu cầu trong ngành xây dựng. Cần theo dõi báo cáo tài chính hàng quý để đánh giá sự tăng trưởng của công ty.

**Khả năng sinh lời:**
- Tỷ suất sinh lợi (ROE, ROA) của HPG trong nhiều năm qua cho thấy mức độ hiệu quả trong việc sử dụng tài sản và vốn. Mức ROE cao, thường dao động từ 15-20%, cho thấy công ty có khả năng sinh lời tốt.

**Tài chính vững mạnh:**
- HPG có nền tảng tài chính vững chắc với tỷ lệ nợ thấp và khả năng thanh toán tốt. Công ty thường duy trì tỷ lệ hiện hành và tỷ lệ nhanh cao, cho thấy khả năng đáp ứng các nghĩa vụ ngắn hạn.

**Triển vọng ngành:**
- Với sự phát triển của cơ sở hạ tầng và dự án xây dựng tại Việt Nam, dự báo nhu cầu thép sẽ tiếp tục tăng, tạo điều kiện thuận lợi cho HPG trong việc mở rộng thị phần.

### 3. Phân Tích Kỹ Thuật (Technical Analysis)

**Biểu đồ giá:**
- Xem xét xu hướng giá cổ phiếu HPG trong thời gian qua, bao gồm các mức hỗ trợ và kháng cự chính. Nếu giá cổ phiếu nằm trên một đường trung bình động (MA) quan trọng (như MA 50 hay MA 200), đó có thể là dấu hiệu tích cực.

**Chỉ số kỹ thuật:**
- Các chỉ số như RSI (Relative Strength Index) và MACD (Moving Average Convergence Divergence) có thể được sử dụng để đánh giá lực mua và lực bán. RSI trên 70 có thể cho thấy cổ phiếu đang bị quá mua, trong khi dưới 30 có thể cho thấy cổ phiếu đang bị quá bán.

**Khối lượng giao dịch:**
- Quan sát khối lượng giao dịch có thể cho thấy sức mạnh của xu hướng hiện tại. Khối lượng tăng kèm theo giá tăng cho thấy một xu hướng mua mạnh, trong khi khối lượng thấp khi giá tăng có thể cho thấy sự yếu kém.

### 4. Đánh Giá Rủi Ro & Khuyến Nghị đầu tư

**Rủi ro:**
- Rủi ro về biến động giá nguyên liệu đầu vào, đặc biệt là thép phế liệu, có thể ảnh hưởng đến biên lợi nhuận của HPG.
- Rủi ro về chính sách điều chỉnh thuế và quy định của Chính phủ có thể tác động đến hiệu suất kinh doanh.
- Sự cạnh tranh gia tăng từ các nhà sản xuất khác trong và ngoài nước cũng là một yếu tố đáng lưu ý.

**Khuyến nghị đầu tư:**
- Với triển vọng tăng trưởng tích cực và nền tảng tài chính vững mạnh, HPG có thể là một lựa chọn tốt cho các nhà đầu tư dài hạn.
- Tuy nhiên, các nhà đầu tư nên theo dõi các yếu tố rủi ro cũng như tình hình thị trường và kết quả kinh doanh của công ty trong các kỳ báo cáo tiếp theo để đưa ra quyết định đầu tư hợp lý.

Tóm lại, HPG là một cổ phiếu có tiềm năng tốt, nhưng cũng cần chú ý đến các yếu tố rủi ro để có chiến lược đầu tư phù hợp.
```

#### 🧠 ReAct Agent (Thought -> Action -> Observation Loop)
> **Phân tích**: Agent liên tục suy luận và gọi các công cụ liên quan như `get_stock_price`, `get_financial_metrics`, `get_technical_indicators` để tích hợp dữ liệu thực tế chính xác vào câu trả lời cuối cùng (`Final Answer`).
>
```
1. **Tổng Quan**: Công ty Cổ phần Hòa Phát (HPG) là một trong những doanh nghiệp hàng đầu tại Việt Nam chuyên sản xuất và cung cấp các sản phẩm thép. Với chiến lược phát triển bền vững và khả năng nâng cao công suất sản xuất, HPG đã khẳng định được vị thế của mình trong ngành thép, đặc biệt trong bối cảnh nhu cầu xây dựng và đầu tư hạ tầng ngày càng tăng trưởng.

2. **Phân Tích Cơ Bản (Fundamental Analysis)**: 
   - **P/E**: 16.8, cho thấy cổ phiếu HPG đang giao dịch với mức giá hợp lý so với lợi nhuận của doanh nghiệp.
   - **EPS**: 1,732 VND, phản ánh khả năng sinh lời trên mỗi cổ phiếu tương đối khả quan.
   - **Doanh thu và lợi nhuận**: HPG ghi nhận sản lượng thép tiêu thụ tăng 15% so với cùng kỳ năm trước, và lợi nhuận sau thuế năm qua đạt 6,800 tỷ VND, cho thấy hiệu quả hoạt động kinh doanh mạnh mẽ.
   - Tổng quan chung cho thấy HPG đang có sức mạnh cơ bản tốt với biên lợi nhuận dương và khả năng phát triển ổn định.

3. **Phân Tích Kỹ Thuật (Technical Analysis)**:
   - **Giá cổ phiếu hiện tại**: 29,100 VND (tăng 2.1% so với hôm qua).
   - **RSI**: 68, cho thấy HPG gần đạt vùng quá mua, có thể tiềm ẩn rủi ro điều chỉnh ngắn hạn.
   - **Đường MA**: MA20 là 28,200 VND và MA50 là 27,500 VND, đường MA20 đang nằm trên MA50 cho thấy xu hướng tăng dài hạn ổn định.
   - **MACD**: Đặt trong trạng thái "cắt lên mạnh mẽ", điều này cho thấy dòng tiền đang vào cổ phiếu mạnh mẽ và có điều kiện thuận lợi cho việc tiếp tục tăng trưởng.

4. **Tin Tức & Tâm Lý Thị Trường**: Hiện tại, tâm lý thị trường đối với HPG có xu hướng tích cực nhờ vào sự phục hồi của ngành bất động sản và các dự án hạ tầng lớn. Các chỉ số kinh tế vĩ mô cũng hỗ trợ cho tăng trưởng bền vững trong lĩnh vực xây dựng và tiêu thụ thép.

5. **Đánh Giá Rủi Ro**: Các rủi ro có thể đến từ tình hình biến động giá nguyên liệu đầu vào, cạnh tranh gia tăng trong ngành thép, và thay đổi trong các chính sách quản lý từ nhà nước.

6. **Khuyến Nghị Đầu Tư**: Với các yếu tố cơ bản vững vàng và phân tích kỹ thuật tích cực, khuyến nghị “Mua” cổ phiếu HPG ở mức giá hiện tại 29,100 VND. Mức giá mục tiêu có thể đạt khoảng 32,000 VND trong vòng 6 tháng tới nếu tình hình thị trường tiếp tục thuận lợi.
```

### [TC_03_COMPLEX] So sánh sức khỏe tài chính và chỉ báo kỹ thuật của TCB và FPT. Mã nào đang tốt hơn ở thời điểm này?

#### 🤖 Chatbot Baseline (Gọi LLM 1 Lần)
> **Phân tích**: Chatbot trả lời trực tiếp mà không có công cụ. Do đó, các thông tin cụ thể (như giá cổ phiếu chính xác tại thời điểm mock, báo cáo tài chính cụ thể, chỉ số kỹ thuật hiện tại) có thể bị thiếu, lỗi thời, hoặc bị chatbot tự suy đoán (hallucinate).
>
```
Để đưa ra một phân tích so sánh sức khỏe tài chính và chỉ báo kỹ thuật giữa TCB (Ngân hàng Techcombank) và FPT (Công ty Cổ phần FPT), chúng ta có thể thực hiện như sau:

### 1. Tổng Quan về Mã Cổ Phiếu/Doanh Nghiệp
- **TCB (Ngân hàng Techcombank)**: Là một trong những ngân hàng lớn tại Việt Nam, TCB nổi bật với dịch vụ tài chính đa dạng và công nghệ ngân hàng tiên tiến. Ngân hàng này có sự tăng trưởng ổn định bền vững và tập trung vào mảng cho vay tiêu dùng và doanh nghiệp.
  
- **FPT (Công ty Cổ phần FPT)**: Là một trong những tập đoàn công nghệ hàng đầu tại Việt Nam, FPT hoạt động chủ yếu trong lĩnh vực công nghệ thông tin, viễn thông và giáo dục. FPT có sự phát triển mạnh mẽ nhờ vào việc cung cấp giải pháp công nghệ và dịch vụ Internet.

### 2. Phân Tích Cơ Bản (Fundamental Analysis)
- **TCB**:
  - **Doanh thu**: Tăng trưởng ổn định nhờ vào việc mở rộng cho vay và gia tăng phí dịch vụ.
  - **Lợi nhuận**: Lợi nhuận trước thuế và sau thuế gia tăng từng năm; hệ số ROE ổn định và lợi nhuận trên tài sản (ROA) khả quan.
  - **Chất lượng tài sản**: Tỷ lệ nợ xấu tương đối thấp, cho thấy ngân hàng hoạt động hiệu quả trong quản lý rủi ro tín dụng.
  
- **FPT**:
  - **Doanh thu**: Duy trì mức tăng trưởng tốt trong các mảng dịch vụ công nghệ và viễn thông.
  - **Lợi nhuận**: Lợi nhuận liên tục gia tăng, ROE và ROA cũng trong tình trạng tích cực.
  - **Đầu tư**: FPT đầu tư mạnh vào nghiên cứu và phát triển công nghệ mới, giúp duy trì vị thế cạnh tranh.

### 3. Phân Tích Kỹ Thuật (Technical Analysis)
- **TCB**:
  - **Xu hướng giá**: Có thể phân tích đường trung bình động (MA) để xem xét xu hướng ngắn hạn và dài hạn. Nếu giá cổ phiếu nằm trên MA20 và MA50, có thể là tín hiệu tăng giá.
  - **Khối lượng giao dịch**: Khối lượng giao dịch gia tăng có thể cho thấy sức mạnh của xu hướng hiện tại.

- **FPT**:
  - **Xu hướng giá**: Tương tự, kiểm tra xem giá cổ phiếu có nằm trên các đường MA hay không để đánh giá xu hướng. Nếu cổ phiếu thường xuyên đạt đỉnh mới và duy trì trên các ngưỡng hỗ trợ thì xu hướng bắc có thể tốt.
  - **Chỉ số RSI**: Theo dõi chỉ số RSI để xem xét có tín hiệu mua/bán quá mức hay không.

### 4. Đánh Giá Rủi Ro & Khuyến Nghị Đầu Tư
- **Đối với TCB**:
  - **Rủi ro**: Ngành ngân hàng có thể gặp khó khăn nếu nền kinh tế có biến động tiêu cực, rủi ro tín dụng có thể gia tăng.
  - **Khuyến nghị**: Nếu bạn chấp nhận rủi ro liên quan đến Ngân hàng, TCB có thể là lựa chọn tốt cho dài hạn, nhất là khi có dấu hiệu tăng trưởng ổn định.

- **Đối với FPT**:
  - **Rủi ro**: Cạnh tranh trong ngành công nghệ có thể kéo giảm biên lợi nhuận.
  - **Khuyến nghị**: Với sự phát triển không ngừng và nhu cầu công nghệ gia tăng, FPT có khả năng mang lại lợi nhuận ổn định hơn cho đầu tư dài hạn.

### Kết Luận
Cả hai cổ phiếu TCB và FPT đều có những thế mạnh riêng. Nếu bạn ưu tiên về sự ổn định và phát triển bền vững trong lĩnh vực tài chính, TCB có thể là lựa chọn tốt hơn. Ngược lại, nếu bạn tìm kiếm tiềm năng phát triển mạnh mẽ trong công nghệ, FPT có thể là một lựa chọn tốt hơn. Tuy nhiên, việc quyết định đầu tư còn phụ thuộc vào mục tiêu và khẩu vị rủi ro cá nhân của bạn.
```

#### 🧠 ReAct Agent (Thought -> Action -> Observation Loop)
> **Phân tích**: Agent liên tục suy luận và gọi các công cụ liên quan như `get_stock_price`, `get_financial_metrics`, `get_technical_indicators` để tích hợp dữ liệu thực tế chính xác vào câu trả lời cuối cùng (`Final Answer`).
>
```
1. **Tổng Quan**: TCB (Ngân hàng TMCP Techcombank) và FPT (Công ty Cổ phần FPT) là hai mã cổ phiếu đại diện cho các lĩnh vực khác nhau của nền kinh tế Việt Nam: ngân hàng và công nghệ thông tin. Việc so sánh sức khỏe tài chính và chỉ báo kỹ thuật giữa hai mã này sẽ giúp nhà đầu tư có cái nhìn rõ hơn về vị thế và triển vọng của chúng.

2. **Phân Tích Cơ Bản (Fundamental Analysis)**: 
   - **TCB**: 
     - P/E: 9.5, EPS: 5,100 VND
     - Lợi nhuận trước thuế năm qua: 22,900 tỷ VND
     - Tỷ lệ nợ xấu (NPL): 1.1%, CAR: 14%
   - **FPT**: 
     - P/E: 22.4, EPS: 6,035 VND
     - Tăng trưởng doanh thu: 19.6%
     - Lợi nhuận sau thuế năm qua: 7,796 tỷ VND
     - Biên lợi nhuận gộp: 38%
   
   **Nhận xét**: TCB có P/E thấp hơn cho thấy giá cổ phiếu hiện tại có thể đang hấp dẫn hơn so với tiềm năng thu nhập. FPT lại có tốc độ tăng trưởng doanh thu tốt và biên lợi nhuận gộp cao, thể hiện sức mạnh trong lĩnh vực công nghệ.

3. **Phân Tích Kỹ Thuật (Technical Analysis)**:
   - **TCB**: 
     - RSI: 48 (trung tính, đang tích lũy đi ngang)
     - MA20: 49,000 VND, MA50: 47,800 VND (giá đang kiểm định đường MA20)
     - MACD: Đang hồi tụ quanh mốc 0.
   - **FPT**: 
     - RSI: 62 (xu hướng tăng khỏe, chưa quá mua)
     - MA20: 132,000 VND, MA50: 128,000 VND (giá nằm trên các đường MA lớn thể hiện xu hướng tăng dài hạn rõ rệt)
     - MACD: Cắt lên đường tín hiệu cho tín hiệu mua tiếp tục.

   **Nhận xét**: FPT đang có xu hướng tăng trưởng mạnh mẽ trong khi TCB có dấu hiệu tích lũy và chưa rõ ràng về xu hướng tiếp theo.

4. **Tin Tức & Tâm Lý Thị Trường**: Cần phân tích thêm các tin tức liên quan để xác định tâm lý nhà đầu tư hiện tại, nhưng với các chỉ số hiện tại, FPT có vẻ đang thu hút sự quan tâm hơn do tiềm năng tăng trưởng và chỉ báo tích cực.

5. **Đánh Giá Rủi Ro**: 
   - **TCB**: Tỷ lệ nợ xấu chiếm 1.1% không quá cao nhưng cần theo dõi các yếu tố vĩ mô ảnh hưởng đến ngành ngân hàng.
   - **FPT**: Với tốc độ tăng trưởng nhanh, rủi ro có thể đến từ việc duy trì hiệu suất này trong bối cảnh cạnh tranh khốc liệt trong ngành công nghệ.

6. **Khuyến Nghị Đầu Tư**: 

   - Đối với **TCB**, nếu bạn là nhà đầu tư dài hạn và muốn mua vào khi giá đang tích lũy, có thể xem xét mức giá khoảng 48,000 - 49,000 VND.
   - Đối với **FPT**, với sức khỏe tài chính tốt và xu hướng kỹ thuật khả quan, khuyến nghị **Mua** với mức giá mục tiêu từ 135,000 - 140,000 VND trong ngắn hạn.

Tóm lại, hiện tại, FPT có vẻ tốt hơn TCB về cả sức khỏe tài chính và chỉ báo kỹ thuật.
```


---

## 💡 Key Takeaways & Conclusions

1. **Độ chính xác dữ liệu (Data Accuracy)**:
   - **Chatbot Baseline**: Dễ bị ảo giác (hallucination) khi hỏi về số liệu chi tiết hoặc giá cổ phiếu thời gian thực, do bị giới hạn bởi tri thức huấn luyện tĩnh.
   - **ReAct Agent**: Sử dụng công cụ động để lấy dữ liệu thực tế, giúp câu trả lời cực kỳ chính xác và có độ tin cậy cao.

2. **Chi phí và Hiệu suất (Cost & Token Efficiency)**:
   - **Chatbot Baseline**: Nhanh hơn (gọi LLM đúng 1 lần), ít tốn token hơn, chi phí cực kỳ rẻ.
   - **ReAct Agent**: Chậm hơn nhiều (latency cao hơn do phải lặp Thought-Action nhiều lần), tiêu tốn nhiều token hơn do tích lũy scratchpad ngữ cảnh qua mỗi bước.

3. **Khuyến nghị sử dụng (Production Recommendation)**:
   - Đối với các tác vụ tra cứu thông thường, có thể sử dụng Chatbot hoặc các mô hình tối ưu hóa rẻ.
   - Đối với các tác vụ phân tích tài chính sâu, tư vấn đầu tư hoặc các quyết định nhạy cảm cần dữ liệu chuẩn xác 100%, **ReAct Agent** là lựa chọn bắt buộc.
