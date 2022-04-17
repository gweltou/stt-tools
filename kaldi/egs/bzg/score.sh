nj=2
decode_cmd="run.pl --mem 4G"

steps/decode.sh --config conf/decode.config --nj $nj --cmd "$decode_cmd" exp/tri1/graph data/test exp/tri1/decode

echo "****** decode_fmllr.sh ******"
    steps/decode_fmllr.sh --nj $nj --cmd "$decode_cmd" \
                          exp/tri3b/graph_tgsmall data/test \
                          exp/tri3b/decode_tgsmall_test


steps/scoring/score_kaldi_cer.sh
